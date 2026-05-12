---
name: ahe-evolution
description: Run the Agentic Harness Engineering evolution loop — evaluate research agent performance, analyze failure traces, and automatically improve harness components (system prompt, tools, middleware, skills, memory). Use when agent performance on research tasks needs systematic improvement, or when setting up automated harness evolution.
---

# AHE Evolution Loop

Automatically evolve the research agent harness through iterative Evaluate → Analyze → Improve cycles. Models stay frozen; the harness learns.

## Context Budget

**MUST load:**
- `skills/ahe-evolution/config/base.yaml` or the experiment overlay being used
- `skills/ahe-evolution/harness/systemprompt.md` — current agent identity and behavior rules
- `skills/ahe-evolution/harness/agent.yaml` — current tool/middleware/skill registration
- `skills/ahe-evolution/tasks/tasks.yaml` — task definitions for this experiment
- Previous iteration's `analysis/overview.md` if resuming

**MUST NOT load:**
- Raw traces in `runs/iteration_NNN/input/results/` (load only when trace_analyzer needs them)
- Unused harness components (only load what the experiment targets)
- Other skills' SKILL.md files unless explicitly referenced by a task

## When to Use

- User asks to "improve the agent" or "run evolution"
- User wants to systematically optimize research task performance
- After adding new skills or tools that need harness-level optimization
- When trace analysis reveals recurring failure patterns

## Architecture

```
EVALUATE               ANALYZE                   IMPROVE
Task Runner →          Trace Analyzer →          Evolve Agent →
  git worktree沙箱         LLM读trace+评分             LLM修改harness/组件
  执行研究任务              找根因→overview.md         写change_manifest
  trace.json+score.json    +detail/{task}.md          git commit+tag
```

### 7 Evolvable Harness Components

| # | Component | File | Evolve Agent Can |
|---|-----------|------|------------------|
| 1 | System Prompt | `harness/systemprompt.md` | Modify agent identity, behavior rules |
| 2 | Agent Config | `harness/agent.yaml` | Register/deregister tools, middleware, skills |
| 3 | Tool Descriptions | `harness/tool_descriptions/*.tool.yaml` | Clarify usage, add examples, warn about pitfalls |
| 4 | Tool Implementations | `harness/tools/*.py` | New capabilities, smarter error handling |
| 5 | Middleware | `harness/middleware/*.py` | Physics thinking injection, gate checks |
| 6 | Skills | `harness/skills/*/` | Reusable workflow patterns |
| 7 | Long-Term Memory | `harness/LongTermMEMORY.md` | Persistent cross-session knowledge |

### Middleware Pipeline

Middleware hooks into the agent execution loop between LLM calls and tool execution:

```
before_model → LLM call → after_model → before_tool → tool execution → after_tool
```

**Physics middleware (always active):**
- `physics_thinking.py` — before_model: inject 5 physics reflex prompts (scale separation, symmetry→constraint, perturbative instinct, phenomenology first, approximation self-awareness)
- `dimensional_check.py` — after_tool: mechanized dimensional analysis on equation outputs
- `limit_check.py` — after_tool: mechanized known-limit regression verification

## Workflow

### Quick Start

```bash
# Run a single experiment
cd skills/ahe-evolution
python evolve.py --config config/experiments/exp-01-baseline.yaml

# Run all experiments in batch
python evolve.py --batch config/experiments/

# Resume interrupted experiment
python evolve.py \
  --experiment 2026-05-11__baseline \
  --start-iteration 3 \
  --config config/experiments/exp-01-baseline.yaml
```

### Step 1: Define Tasks

Edit `tasks/tasks.yaml` to define what the agent should do and how to score it. Each task specifies:
- `skill`: which research skill to evaluate (paper-to-insight, state-overview, derivation-tracker)
- `input`: what data/parameters to give the agent
- `scoring.dimensions`: mechanized quality checks with weights

### Step 2: Configure Experiment

Create a config overlay in `config/experiments/` that inherits from `config/base.yaml`:

```yaml
_base: "../base.yaml"

_name: "my-experiment"
_target_quality: 0.85
max_iterations: 10

evolvable_components:
  systemprompt_md: true
  skills: true
```

### Step 3: Run Evolution

`evolve.py` orchestrates the full loop:
1. **Evaluate**: Task Runner executes agent in git worktree sandbox, records traces + scores
2. **Analyze**: Trace Analyzer reads traces, identifies root causes, writes analysis reports
3. **Improve**: Evolve Agent reads analysis, modifies harness components, commits changes
4. **Repeat** until target quality reached or max iterations exhausted

### Step 4: Review Results

Output in `agent-workspace/ahe-experiments/<exp-name>/`:
- `iteration_scores.yaml` — scores per iteration
- `evolution_history.md` — full narrative of what changed and why
- `runs/iteration_NNN/input/analysis/overview.md` — per-iteration root cause analysis

## Key Rules

1. **Gate = mechanized check, never LLM self-eval** — dimensional analysis, limit regression, file existence, frontmatter completeness are all script-verifiable
2. **Every change must cite failure evidence** — no change without a specific trace showing the failure
3. **Evolve agent modifies only `workspace/`** — the harness components, nothing outside
4. **Rollback on regression** — if quality drops significantly, auto-restore best-known workspace
5. **Start locked, unlock gradually** — first run locks all components; evolve agent only writes analysis. Then unlock systemprompt.md → skills → tools → middleware.

## Source Grounding

- Every change recorded in `change_manifest.json` must link to a specific task trace
- Mechanized checkers cite the rule they enforce (dimensional analysis rules, known-limit pairs)
- Analysis reports cite line numbers in traces, not summaries of summaries
