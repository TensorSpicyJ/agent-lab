"""
Evolve Agent — Phase 3 of the AHE evolution loop.

A meta-agent that reads analysis reports and modifies harness components
in the workspace. Each change must cite failure evidence and predict impact.

Produces:
  - evolve_summary.md — narrative of what was changed and why
  - change_manifest.json — structured change log for attribution
  - Git commit with iteration tag
"""

import json
from datetime import datetime, timezone
from pathlib import Path

import yaml

from shared.git_utils import commit_workspace


# ═══════════════════════════════════════════════════════
# Evolution Query Builder
# ═══════════════════════════════════════════════════════

def build_evolution_query(
    iteration: int,
    analysis_overview: str,
    task_results: dict[str, dict],
    evolution_history: str,
    previous_manifest: dict | None,
    evolvable_components: dict[str, bool],
) -> str:
    """Build the evolution prompt for the evolve agent.

    Args:
        iteration: Current iteration number
        analysis_overview: The overview.md content from trace analysis
        task_results: {task_id: {"score": ..., "status": ...}}
        evolution_history: Content of evolution_history.md (prior changes)
        previous_manifest: Previous iteration's change_manifest.json (for attribution)
        evolvable_components: Which components the agent may modify
    """
    evolvable_list = "\n".join(
        f"- {comp}: {'UNLOCKED' if unlocked else 'LOCKED'}"
        for comp, unlocked in evolvable_components.items()
    )

    task_summary = "\n".join(
        f"- {tid}: score={info.get('score', '?')}, status={info.get('status', '?')}"
        for tid, info in sorted(task_results.items())
    )

    prev_changes = "None (first iteration)"
    if previous_manifest:
        prev_changes = json.dumps(previous_manifest, ensure_ascii=False, indent=2)

    return f"""## Evolution Iteration {iteration}

### Current Task Results
{task_summary}

### Analysis Report
{analysis_overview}

### Evolution History
{evolution_history if evolution_history else 'No prior changes.'}

### Previous Iteration Changes (for attribution)
```json
{prev_changes}
```

### Evolvable Components
{evolvable_list}

### Instructions

You are the Evolve Agent. Your job is to improve the research agent harness
based on the analysis above.

**Rules:**
1. ONLY modify unlocked components listed above
2. Every change MUST cite specific failure evidence from the analysis
3. Every change MUST predict which tasks it will fix
4. Do NOT modify LLM config, infrastructure, or files outside workspace/
5. Do NOT add task-specific logic or hardcoded solutions
6. Write changes directly to files in workspace/

**For each change:**
1. Read the target file(s) first
2. Make the minimal edit needed
3. Verify the file is still valid (YAML parses, Python compiles)

**After all changes, produce:**
1. `evolve_summary.md` — what you changed and why
2. `change_manifest.json` — structured change log (format below)

```json
{{
  "iteration": {iteration},
  "changes": [
    {{
      "id": "chg-1",
      "type": "improvement|new|rollback",
      "description": "What was changed and why",
      "files": ["relative/path/to/file"],
      "component": "systemprompt_md|skills|tool_descriptions|tools|middleware|long_term_memory|agent_yaml",
      "failure_pattern": "The failure class this addresses",
      "predicted_fixes": ["task-id-1"],
      "risk_tasks": [],
      "rationale": "Why this change at this component level"
    }}
  ]
}}
```

Date: {datetime.now().strftime('%Y-%m-%d')}
"""


# ═══════════════════════════════════════════════════════
# Evolve Agent
# ═══════════════════════════════════════════════════════

class EvolveAgent:
    """Meta-agent that modifies harness components based on analysis."""

    def __init__(self, llm_config: dict):
        self.llm_config = llm_config

    def evolve(
        self,
        workspace_dir: Path,
        iteration_dir: Path,
        iteration: int,
        analysis_overview: str,
        task_results: dict[str, dict],
        evolution_history: str,
        previous_manifest: dict | None,
        evolvable_components: dict[str, bool],
        dry_run: bool = False,
    ) -> dict:
        """Run the evolve step.

        In dry_run mode, the analyze-report-only strategy is used:
        only writes evolve_summary.md without modifying harness files.
        """
        evolve_dir = iteration_dir / "evolve"
        evolve_dir.mkdir(parents=True, exist_ok=True)

        query = build_evolution_query(
            iteration, analysis_overview, task_results,
            evolution_history, previous_manifest, evolvable_components,
        )

        if dry_run:
            # No LLM call — just write placeholder evolve output
            summary = _build_dry_run_summary(analysis_overview, evolvable_components)
            manifest = {"iteration": iteration, "changes": []}
        else:
            result = self._call_evolve_llm(query, workspace_dir)
            summary = result.get("summary", "")
            manifest = result.get("manifest", {"iteration": iteration, "changes": []})

        # Write outputs
        summary_path = evolve_dir / "evolve_summary.md"
        summary_path.write_text(summary, encoding="utf-8")

        manifest_path = iteration_dir.parent / "change_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)

        # Git commit
        commit_hash = commit_workspace(
            workspace_dir,
            message=f"Iteration {iteration}: {len(manifest.get('changes', []))} changes",
            tag=f"iteration-{iteration:03d}",
        )

        return {
            "summary": summary,
            "manifest": manifest,
            "commit": commit_hash,
            "summary_path": str(summary_path),
            "manifest_path": str(manifest_path),
        }

    def _call_evolve_llm(self, query: str, workspace_dir: Path) -> dict:
        """Call the LLM to evolve harness components."""
        from openai import OpenAI

        client = OpenAI(
            base_url=self.llm_config.get("base_url", "https://api.deepseek.com"),
            api_key=self.llm_config.get("api_key", ""),
        )
        model = self.llm_config.get("model", "deepseek-chat")

        # Read current harness state to include in context
        harness_context = _read_harness_state(workspace_dir)

        try:
            resp = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _get_evolve_system_prompt(workspace_dir, harness_context)},
                    {"role": "user", "content": query},
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            content = resp.choices[0].message.content or ""
        except Exception as e:
            print(f"  [evolve] LLM call failed: {e}")
            return {"summary": f"LLM call failed: {e}", "manifest": {"iteration": 0, "changes": []}}

        # Extract JSON manifest if embedded in response
        manifest = _extract_manifest(content, query)
        return {"summary": content, "manifest": manifest}


def _read_harness_state(workspace_dir: Path) -> str:
    """Read key harness files for context in the evolution prompt."""
    files = {}
    key_files = ["systemprompt.md", "agent.yaml", "LongTermMEMORY.md"]
    for name in key_files:
        f = workspace_dir / name
        if f.exists():
            content = f.read_text(encoding="utf-8")
            if len(content) > 3000:
                content = content[:3000] + "\n... (truncated)"
            files[name] = content
    return "\n\n".join(f"### {name}\n```\n{content}\n```" for name, content in files.items())


def _get_evolve_system_prompt(workspace_dir: Path, harness_context: str) -> str:
    return f"""You are the Evolve Agent — a meta-agent that improves research agent harnesses.

Your workspace: {workspace_dir}/

You have tools to read and write files. For each change:
1. Read the target file first (use read_file)
2. Apply the minimal edit (use write_file)
3. Verify validity

## Current Harness State
{harness_context}

## Rules
- Only modify files under workspace_dir
- Each change must target a specific failure pattern from analysis
- Do NOT modify LLM config (model, temperature, etc.)
- Do NOT add task-specific logic
- After all changes, produce evolve_summary.md and change_manifest.json
"""


def _extract_manifest(text: str, query: str) -> dict:
    """Try to extract a JSON change manifest from LLM response."""
    import re
    # Look for {...} JSON block containing "iteration" and "changes"
    pattern = re.compile(r'\{[^{}]*"iteration"[^{}]*"changes"[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', re.DOTALL)
    matches = pattern.findall(text)
    for match in matches:
        try:
            return json.loads(match)
        except json.JSONDecodeError:
            continue

    # Fallback: extract iteration number from query
    iter_match = re.search(r'"iteration":\s*(\d+)', text)
    iteration = int(iter_match.group(1)) if iter_match else 0
    return {"iteration": iteration, "changes": []}


def _build_dry_run_summary(analysis_overview: str, evolvable_components: dict) -> str:
    """Build a placeholder evolve summary when no components are unlocked."""
    locked = [c for c, unlocked in evolvable_components.items() if not unlocked]
    return f"""## Evolution Summary (Dry Run)

All harness components are locked. No changes were made.

### Analysis
{analysis_overview[:2000]}

### Locked Components
{', '.join(locked)}

### Next Steps
Unlock components in the experiment config to enable evolution.
Start with `systemprompt_md: true` and `long_term_memory: true`.
"""
