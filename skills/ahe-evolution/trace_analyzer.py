"""
Trace Analyzer — Phase 2 of the AHE evolution loop.

Takes task execution results (traces + scores), builds analysis prompts,
and calls an LLM to identify root causes of failures. Produces:
  - analysis/overview.md — cross-task root cause summary
  - analysis/detail/{task_id}.md — per-task deep analysis

This is the simplest viable version: one LLM call per low-scoring task.
Future: batch analysis, cross-task pattern mining.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml


# ═══════════════════════════════════════════════════════
# Analysis Query Builder
# ═══════════════════════════════════════════════════════

def build_task_analysis_query(task_id: str, task_config: dict, trace: list, score: dict) -> str:
    """Build an analysis prompt for a single task."""
    score_str = json.dumps(score, ensure_ascii=False, indent=2) if score else "no score"
    trace_summary = _summarize_trace(trace)

    return f"""## Task Analysis: {task_id}

### Task Definition
- Name: {task_config.get('name', task_id)}
- Skill: {task_config.get('skill', 'unknown')}
- Description: {task_config.get('description', 'no description')}

### Quality Score
```json
{score_str}
```

### Agent Trace Summary
{trace_summary}

### Analysis Instructions

Identify the root cause of any quality gaps. For each gap:

1. **ROOT CAUSE**: Why did the agent score low on specific dimensions?
   - Was it a prompt issue (agent didn't understand what to do)?
   - Was it a tool issue (right intent, wrong execution)?
   - Was it a skill issue (missing workflow guidance)?
   - Was it a knowledge issue (didn't load necessary context)?

2. **FAILURE PATTERN**: What class of error is this?
   - source_grounding: agent made claims without citing sources
   - template_incompleteness: agent skipped required sections
   - cross_reference: agent linked to wrong hypotheses
   - behavior: agent called wrong tools or wrong sequence
   - completion: agent didn't finish the task

3. **SUGGESTED FIX**: What should change and where?
   - Which harness component: systemprompt.md / tool_descriptions/ / skills/ / tools/ / middleware/ / LongTermMEMORY.md
   - What specific change?

4. **PREDICTED IMPACT**: Which other tasks might benefit or regress from this fix?

Respond in structured markdown. Be specific — cite trace evidence (turn numbers, tool calls).
"""


def build_overview_query(task_analyses: dict[str, str], overall_score: float) -> str:
    """Build an analysis prompt for the cross-task overview."""
    task_list = "\n".join(f"- {tid}" for tid in sorted(task_analyses))
    analyses_text = "\n\n---\n\n".join(
        f"### {tid}\n{analysis}" for tid, analysis in sorted(task_analyses.items())
    )

    return f"""## Iteration Overview Analysis

### Overall Quality: {overall_score:.3f}
### Tasks Analyzed: {len(task_analyses)}

### Per-Task Analyses
{analyses_text}

### Instructions

Synthesize findings across all tasks:

1. **Recurring failure patterns** — which patterns appear in 2+ tasks?
2. **Priority ranking** — which fixes would have the broadest impact?
3. **Cross-component insights** — are failures clustering in specific harness components?
4. **Recommended changes** — top 3-5 changes, ordered by predicted impact.
5. **Risk assessment** — which tasks might regress from the recommended changes?

Write a concise overview (under 3000 words). Start with "## Overview" and end with "## Recommended Changes".
"""


def _summarize_trace(trace: list) -> str:
    """Summarize agent trace into a compact text block for the analyzer."""
    lines = []
    for entry in trace:
        turn = entry.get("turn", "?")
        llm = entry.get("llm_call", {})
        if llm.get("content"):
            lines.append(f"Turn {turn} [Agent]: {llm['content'][:200]}")

        for tc in llm.get("tool_calls", []):
            lines.append(f"Turn {turn} [ToolCall]: {tc['name']}({tc['arguments'][:150]})")

        for te in entry.get("tool_executions", []):
            lines.append(f"Turn {turn} [ToolResult]: {te['name']} → {str(te['result'])[:200]}")
            if te.get("warnings"):
                for w in te["warnings"]:
                    lines.append(f"Turn {turn} [Warning]: {str(w)[:200]}")

        for ma in entry.get("middleware_actions", []):
            lines.append(f"Turn {turn} [Middleware:{ma['hook']}]: {str(ma.get('warnings', ''))[:200]}")

    return "\n".join(lines[:100])  # cap at ~100 trace lines


# ═══════════════════════════════════════════════════════
# Trace Analyzer
# ═══════════════════════════════════════════════════════

class TraceAnalyzer:
    """Analyze task execution traces to identify failure root causes."""

    def __init__(self, llm_config: dict | None = None):
        """
        Args:
            llm_config: {"api_key": ..., "base_url": ..., "model": ...}
                        If None, analysis is done without LLM (pattern-based only).
        """
        self.llm_config = llm_config

    def analyze(
        self,
        results_dir: Path,
        tasks: list[dict],
        output_dir: Path,
    ) -> dict:
        """Analyze all task traces and write reports.

        Returns:
            {"overview_path": ..., "details": {task_id: detail_path, ...}}
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        detail_dir = output_dir / "detail"
        detail_dir.mkdir(parents=True, exist_ok=True)

        # Collect task results
        task_analyses = {}
        task_scores = {}

        for task_config in tasks:
            task_id = task_config["id"]
            result_file = results_dir / task_id / "result.json"
            trace_file = results_dir / task_id / "rollout_1" / "trace.json"
            score_file = results_dir / task_id / "rollout_1" / "score.json"

            if not result_file.exists():
                print(f"  [analyzer] No results for {task_id}, skipping")
                continue

            result = json.loads(result_file.read_text(encoding="utf-8"))
            trace = json.loads(trace_file.read_text(encoding="utf-8")) if trace_file.exists() else []
            score = json.loads(score_file.read_text(encoding="utf-8")) if score_file.exists() else None

            overall_score = score.get("overall_score", 0.0) if score else 0.0
            task_scores[task_id] = overall_score

            # Only deep-analyze tasks below quality threshold
            if overall_score < 0.8:
                analysis = self._analyze_task(task_id, task_config, trace, score)
                task_analyses[task_id] = analysis
                detail_path = detail_dir / f"{task_id}.md"
                detail_path.write_text(analysis, encoding="utf-8")
            else:
                task_analyses[task_id] = f"## {task_id}\nScore {overall_score:.3f} — above threshold, skipped deep analysis."
                (detail_dir / f"{task_id}.md").write_text(task_analyses[task_id], encoding="utf-8")

        # Generate overview
        overall_score = sum(task_scores.values()) / len(task_scores) if task_scores else 0.0
        overview = self._build_overview(task_analyses, overall_score)
        overview_path = output_dir / "overview.md"
        overview_path.write_text(overview, encoding="utf-8")

        return {
            "overview_path": str(overview_path),
            "details": {tid: str(detail_dir / f"{tid}.md") for tid in task_analyses},
            "overview_text": overview,
        }

    def _analyze_task(self, task_id: str, task_config: dict, trace: list, score: dict | None) -> str:
        """Analyze a single task — pattern-based when no LLM config, LLM-based otherwise."""
        if self.llm_config:
            return self._llm_analyze(task_id, task_config, trace, score)
        return self._pattern_analyze(task_id, task_config, trace, score)

    def _llm_analyze(self, task_id: str, task_config: dict, trace: list, score: dict | None) -> str:
        """Use LLM to analyze task trace."""
        from openai import OpenAI

        client = OpenAI(
            base_url=self.llm_config.get("base_url", "https://api.deepseek.com"),
            api_key=self.llm_config.get("api_key", ""),
        )
        model = self.llm_config.get("model", "deepseek-chat")

        query = build_task_analysis_query(task_id, task_config, trace, score)
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You analyze agent execution traces to find root causes of failures. Be specific and cite evidence from the trace."},
                    {"role": "user", "content": query},
                ],
                temperature=0.2,
                max_tokens=2000,
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            print(f"  [analyzer] LLM call failed for {task_id}: {e}")
            return self._pattern_analyze(task_id, task_config, trace, score)

    def _pattern_analyze(self, task_id: str, task_config: dict, trace: list, score: dict | None) -> str:
        """Pattern-based fallback analysis (no LLM required)."""
        lines = [f"## {task_id}", ""]
        dimension_scores = score.get("dimensions", {}) if score else {}

        # Rank dimensions by score
        ranked = sorted(dimension_scores.items(), key=lambda x: x[1].get("score", 0))
        for dim_name, dim_data in ranked[:3]:
            dim_score = dim_data.get("score", 0)
            if dim_score < 0.8:
                lines.append(f"### Low: {dim_name} ({dim_score:.2f})")
                lines.append(f"Details: {dim_data.get('details', 'no details')}")
                lines.append("")
                lines.append(f"**Likely root cause**: {_suggest_root_cause(dim_name, dim_score)}")
                lines.append(f"**Suggested component**: {_suggest_component(dim_name)}")
                lines.append("")

        if not lines[1:]:
            lines.append("All dimensions above threshold. No issues found.")

        return "\n".join(lines)

    def _build_overview(self, task_analyses: dict[str, str], overall_score: float) -> str:
        """Build cross-task overview."""
        if self.llm_config and len(task_analyses) > 1:
            try:
                from openai import OpenAI
                client = OpenAI(
                    base_url=self.llm_config.get("base_url", "https://api.deepseek.com"),
                    api_key=self.llm_config.get("api_key", ""),
                )
                model = self.llm_config.get("model", "deepseek-chat")
                query = build_overview_query(task_analyses, overall_score)
                resp = client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You synthesize multiple task analyses into a concise cross-task overview."},
                        {"role": "user", "content": query},
                    ],
                    temperature=0.2,
                    max_tokens=2000,
                )
                return resp.choices[0].message.content or ""
            except Exception:
                pass

        # Pattern-based fallback overview
        task_list = "\n".join(f"- {tid}" for tid in sorted(task_analyses))
        return f"""## Analysis Overview

**Overall Quality Score**: {overall_score:.3f}

### Analyzed Tasks
{task_list}

### Notes
Pattern-based analysis was used. To enable LLM-based analysis, configure
`trace_analyzer.llm_config` with API credentials in the experiment config.
"""


def _suggest_root_cause(dim_name: str, score: float) -> str:
    """Heuristic root cause suggestion based on dimension name."""
    mapping = {
        "source_grounding": "Agent is not citing sources. Check if system prompt emphasizes source grounding, and if tool descriptions give examples of citation format.",
        "template_completeness": "Agent is skipping required template sections. Check if the skill SKILL.md clearly specifies all required sections.",
        "cross_reference_accuracy": "Agent is linking to wrong hypotheses. Check if hypotheses.md format is clear and if the state-overview skill loads the right context.",
        "knowledge_update_quality": "Agent is not updating knowledge layer files. Check if write_file tool has correct path resolution and if agent knows which files to update.",
        "fact_accuracy": "Agent is making unsupported claims. Check if it reads source material before writing.",
        "completeness": "Agent output is missing key sections. Skill workflow may need more explicit step-by-step guidance.",
        "source_traceability": "Agent statements lack traceable source paths. System prompt may need to enforce source-per-claim rule.",
        "lemma_dependency": "Agent not tracking lemma statuses. Derivation-tracker skill needs explicit lemma scanning step.",
        "gap_detection": "Agent missed derivation gaps. Skill needs explicit gap classification instructions.",
    }
    return mapping.get(dim_name, f"Low score on {dim_name}. Review corresponding skill and tool descriptions.")


def _suggest_component(dim_name: str) -> str:
    """Heuristic component suggestion based on dimension name."""
    mapping = {
        "source_grounding": "systemprompt.md or tool_descriptions/",
        "template_completeness": "skills/{skill}/SKILL.md",
        "cross_reference_accuracy": "skills/state-overview/SKILL.md",
        "knowledge_update_quality": "skills/paper-to-insight/SKILL.md",
        "fact_accuracy": "systemprompt.md (add verify-before-writing rule)",
        "completeness": "skills/{skill}/SKILL.md",
        "source_traceability": "systemprompt.md",
        "lemma_dependency": "skills/derivation-tracker/SKILL.md",
        "gap_detection": "skills/derivation-tracker/SKILL.md",
    }
    return mapping.get(dim_name, "review relevant skill and system prompt")
