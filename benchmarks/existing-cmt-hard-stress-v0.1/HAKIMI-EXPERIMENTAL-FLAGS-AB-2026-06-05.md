# Hakimi Experimental Flags A/B Audit 2026-06-05

## Conclusion

This is the first clean local A/B slice for Hakimi `0.13.0` with the same DeepSeek provider/model in both modes. The experimental switch is confirmed to change the runtime surface: default ON enables seven flags, while the OFF mode logs `flags=[]`; the observed tool surface dropped from 25 tools to 20 tools, and the system prompt became shorter.

On the two probed CMT items, there is no accuracy win yet. Both modes failed both item-mode checks, but for different reasons:

- Problem 1 (`cmt_vmc_rnn_gradient_choices`): default ON did not emit parseable JSON in the clean run; flags OFF emitted JSON but answered `b` against gold `d;e`. This item should be treated as source/gold high-risk before using it as clean model-failure evidence, because option `b` is the standard missing-baseline concern for VMC gradients while the source row marks `d;e`.
- Problem 7 (`cmt_long_range_dqmc_sign_free`): both modes emitted JSON but were wrong. Default ON returned the subset `g` after a much longer run; flags OFF returned the overbroad set `a;b;f;g`.

The runner itself also had a real harness bug during earlier attempts: PowerShell `ConvertTo-Json` was hanging when values were piped through string arrays from flag log lines. The fixed runner now uses `ConvertTo-Json -InputObject` and produced complete `run-metadata.json` files for both clean A/B runs.

## Runtime Surface

| Mode | Experimental flag log | Tool count | System prompt chars | Interpretation |
| --- | --- | ---: | ---: | --- |
| default ON | `physics-memory`, `research-ledger`, `research-action`, `domain-profile`, `workflow-recipe`, `research-harness`, `goal-command` | 25 | observed around 14743-16341 | Current Hakimi experimental mode with additional research/goal/memory tools. |
| default-on flags OFF | `flags=[]` | 20 | observed around 14689-14690 | Same DeepSeek model with default-on experimental flags disabled. |

## Clean A/B Runs

| Problem | Field | Mode | Runtime | JSON | Actual | Expected | Primary attribution |
| ---: | --- | --- | ---: | --- | --- | --- | --- |
| 1 | `cmt_vmc_rnn_gradient_choices` | default ON | 80.043 s | no | prose `b`, no parseable JSON | `d;e` | `model_behavior` |
| 1 | `cmt_vmc_rnn_gradient_choices` | flags OFF | 80.051 s | yes | `b` | `d;e` | `data_source` with `answer_accuracy` secondary |
| 7 | `cmt_long_range_dqmc_sign_free` | default ON | 620.406 s | yes | `g` | `d;g` | `answer_accuracy` |
| 7 | `cmt_long_range_dqmc_sign_free` | flags OFF | 240.144 s | yes | `a;b;f;g` | `d;g` | `answer_accuracy` |

## Evidence Paths

- Problem 1 run: `D:\Playground\agent-lab\benchmarks\existing-cmt-hard-stress-v0.1\runs\20260605-202807__hakimi013_deepseek_flags_ab__cmt_hard_research_8__p1_runner_fix_smoke4`
- Problem 7 run: `D:\Playground\agent-lab\benchmarks\existing-cmt-hard-stress-v0.1\runs\20260605-203143__hakimi013_deepseek_flags_ab__cmt_hard_research_8__p7_runner_fix_smoke`
- Gold file: `D:\Playground\agent-lab\benchmarks\existing-cmt-hard-stress-v0.1\tasks\cmt-hard-research-8\private\gold.json`
- Source file: `D:\Playground\agent-lab\benchmarks\existing-cmt-hard-stress-v0.1\source-cmt_data.jsonl`
- Runner: `D:\Playground\agent-lab\benchmarks\existing-cmt-hard-stress-v0.1\run-hakimi-experimental-ab.ps1`

## Attribution Counts

The clean slice has four item-mode checks:

- `model_behavior`: 1, from default ON p1 failing the output contract.
- `data_source`: 1, from p1 gold/source risk. This is not counted as a clean model capability failure.
- `answer_accuracy`: 2 primary failures, from p7 in both modes; p1 flags OFF also has secondary answer-accuracy uncertainty if the gold is kept.
- `harness`: 1 fixed runner issue outside the four item-mode checks.

## Interpretation

The experimental feature switch is real and observable, but the current data is too small and too noisy to conclude that the experimental mode improves CMT reasoning. It changes the context/tool environment and can change latency and answer shape. In this slice, default ON was worse on JSON emission for p1 and slower on p7, while flags OFF was more concise but over-selected choices on p7.

Problem 1 remains a source-quality boundary. The source row says `\boxed{d;e}`, but the prompt explicitly includes option `b` for the missing-baseline issue, which is a plausible standard criticism of the displayed estimator. This row should be quarantined or manually adjudicated before it contributes to an A/B capability score.

Problem 7 is cleaner as a capability probe: both modes produced parseable JSON and both missed the gold set. Default ON narrowed to `g`, while flags OFF generalized the sign-free criterion too broadly to `a;b;f;g`.

## Recommended Iterations

- `harness`: Keep the `ConvertTo-Json -InputObject` fix and always require `run-metadata.json` plus `live-stage.json` for A/B runs. Retest by running another multi-item slice and checking that summary writing completes.
- `model_behavior`: Strengthen the final output contract so stdout must end with exactly one JSON object. Retest p1 default ON and measure parseable JSON capture.
- `data_source`: Manually review source index 13 before using p1 as a benchmark item. Retest p1 only after gold adjudication.
- `answer_accuracy`: Build a focused DQMC sign-free probe around source index 27. Retest p7 in both modes and compare exact choice sets, not just JSON emission.
- `experiment_design`: Expand from this 2-item slice to all 8 `cmt-hard-research-8` fields after the fixed runner. Repeat at least one item per mode to separate stochastic model variance from feature-switch effects.

## Expansion Attempt Notes

After the clean two-item slice, the runner was extended and probed on larger slices. These attempts are not counted as the clean A/B result above, but they are important harness and model-behavior evidence.

### Fixed During Expansion

- JSON extraction bug fixed: the original extractor used a greedy `\{.*\}` regex. It misread physics text such as `O(e^{-N})` as JSON before the final fenced JSON. The runner now prefers fenced JSON and then scans balanced parseable JSON objects.
- Summary serialization bug remained fixed: `Write-JsonFile` uses `ConvertTo-Json -InputObject`.
- Per-item `MaxRuntimeMinutes` was added so a model that keeps emitting reasoning without finalizing can be recorded as `max_runtime_timeout`.
- Best-effort process-tree termination was added for timeout cases.

### Expansion Evidence

| Run | Scope | Status | What it showed |
| --- | --- | --- | --- |
| `20260605-205624__hakimi013_deepseek_flags_ab__cmt_hard_research_8__full8_flags_ab_20260605b` | full 1-8 attempt | stopped | Pre-fix extractor missed p2 JSON because of `O(e^{-N})`; default ON p1/p2 had JSON in stdout but p2 was falsely marked uncaptured. |
| `20260605-210643__hakimi013_deepseek_flags_ab__cmt_hard_research_8__full8_flags_ab_extractor_fix_20260605` | full 1-8 attempt | stopped | Extractor fix worked for p1-p5; default ON p5 produced the exact numeric vector with substantial derivation. p6 showed long reasoning/finalization pressure. |
| `20260605-213933__hakimi013_deepseek_flags_ab__cmt_hard_research_8__full8_flags_ab_maxruntime_20260605` | full 1-8 attempt | partial | Default ON p1-p5 completed and captured JSON; p6 hit `max_runtime_timeout`; p7 completed without captured stdout JSON in this run; p8 produced reasoning but runner did not finalize the item. |
| `20260605-220247__hakimi013_deepseek_flags_ab__cmt_hard_research_8__p6to8_flags_ab_treekill_20260605` | p6-p8 slice | partial | p6 timed out cleanly and advanced; p7 completed with JSON `b;d;g`; p8 produced answer `a;c` in stderr but the PowerShell/CLI process boundary did not return completion. |

### Updated Attribution

- The full 8-field A/B is not yet a first-version benchmark result. It is currently blocked by harness process-boundary behavior on Windows: `Start-Process` launches `hakimi.CMD` via `cmd.exe`, which launches Node. Some runs produce a final answer, but the parent runner still waits and does not write item completion.
- This is a harness blocker, not an API quota problem and not empty running. Logs show sustained model reasoning and final answers in several cases.
- Default ON p7 is stochastic across runs under the same provider/model/flag family: clean p7 returned `g`, the p6-p8 slice returned `b;d;g`, and flags OFF previously returned `a;b;f;g`. Do not interpret any single p7 run as a stable feature-switch delta.
- Default ON p5 is a capability-supported success candidate: it returned `[0.2, 0.003, 0.017, 0.027, 0.038]`, matching gold, after a long numeric/physics derivation. This should be reviewed as genuine capability evidence rather than counted as a lucky short choice hit.
- Default ON p6 is a model finalization/efficiency failure under the current prompt: it generated long sign-problem reasoning but did not emit final parseable JSON before the runtime cap.

### Next Harness Decision

Before running more A/B batches, replace the PowerShell `Start-Process` wrapper for item execution with a more controllable launcher:

- Prefer a direct Node/Python watchdog that starts the command, reads stdout/stderr asynchronously, kills the whole process tree on timeout, and writes an item result even when the child process does not exit cleanly.
- Alternatively invoke `node ...\dist\main.mjs` directly instead of `hakimi.CMD` to remove the `cmd.exe` layer.
- Keep `live-stage.json`, `run-metadata.partial.json`, and per-item stdout/stderr as mandatory evidence.
