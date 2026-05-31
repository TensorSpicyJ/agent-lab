# QDev vs AHE Co-Evolution

Date: 2026-05-29

## Scope

This note treats "qdev" as the Amazon Q Developer / Q Developer CLI custom-agent style plan, because no local `qdev` design document was found under `D:\Playground\agent-lab` or nearby `D:\Playground` project folders.

If a different private qdev document exists, rerun this comparison against that source.

## Short Conclusion

QDev-style co-evolution is mostly developer-facing context engineering: prompts, tools, permissions, MCP servers, and project/team-specific agent configs evolve with the developer workflow.

Our AHE design is benchmark-driven harness evolution: tasks are evaluated, traces are analyzed, harness components are changed, and those changes are attributed and rolled back if they regress quality.

## Key Differences

| Axis | QDev-style plan | Our AHE / research-agent plan |
| --- | --- | --- |
| Primary object being improved | Custom agents for software development contexts | Research-agent harness and scientific knowledge workflow |
| Evolution trigger | Human updates configs/prompts/tools as workflows change | Evaluate -> Analyze -> Improve loop over task traces |
| Quality signal | Developer judgment, successful task completion, tool permissions | Mechanized scores, trace analysis, change attribution, rollback |
| Memory model | Static context files and dynamic context hooks | Research knowledge layer: `STATE.md`, hypotheses, open questions, papers, experiments, derivations |
| Safety model | Tool allowlists, path permissions, trust settings | Sandbox, locked components, evidence-cited edits, mechanized gates, regression rollback |
| Domain specificity | General coding / AWS / project workflows | Condensed-matter research, physics thinking, dimensional and limit checks |
| Shareability | Project/global custom agents shared across teams | Repo-native Markdown skills, knowledge files, harness configs, experiment histories |

## What QDev Has That We Should Steal

- A clean custom-agent profile format: one file defines prompt, tools, context, and permissions.
- Explicit tool/path permission UX.
- First-class MCP integration as a tool expansion surface.
- Static plus dynamic context hooks.
- Easy switching between specialized agents.

## What We Have That QDev Does Not Emphasize

- Score-driven self-improvement rather than only user-maintained prompt/config iteration.
- Failure-evidence requirement for every harness change.
- Change attribution across iterations.
- Automatic rollback on quality regression.
- Scientific source grounding and domain gates.

## Practical Direction

Do not replace AHE with qdev. Use qdev-style custom-agent profiles as the inner packaging layer, and keep AHE as the outer scientific evolution loop.

Suggested next design slice:

1. Add `harness/agents/` profiles for `paper-reader`, `derivation-worker`, `experiment-analyzer`, and `state-overview`.
2. Put per-agent tool permissions and context budgets in those profiles.
3. Add dynamic context hooks that load the relevant `knowledge/lines/<line>/STATE.md`.
4. Continue using AHE task scores, trace analysis, attribution, and rollback as the actual co-evolution mechanism.
