# Run Summary

- benchmark: `existing-physlib-formal-lane-v0.1`
- task: `physlib-meta-smoke-mini-3`
- agent: `kimi26_code_allowed`
- model alias: `kimi-code/kimi-for-coding`
- local display note: `Kimi-k2.6`
- kimi version: `0.5.0`
- result: `3/3`
- hard_score: `1.0000`
- status: `verified`
- runtime_seconds: `26.55`

Artifacts:
- output: `D:/Playground/agent-lab/benchmarks/existing-physlib-formal-lane-v0.1/runs/20260602-234928__kimi26_code_allowed__physlib_formal_smoke3/outputs/physlib-meta-smoke-mini-3.md`
- score: `D:/Playground/agent-lab/benchmarks/existing-physlib-formal-lane-v0.1/runs/20260602-234928__kimi26_code_allowed__physlib_formal_smoke3/scores/physlib-meta-smoke-mini-3.score.json`
- metadata: `D:/Playground/agent-lab/benchmarks/existing-physlib-formal-lane-v0.1/runs/20260602-234928__kimi26_code_allowed__physlib_formal_smoke3/run-metadata.json`

Scope note:
- This is a `formal-smoke` task over PhysLib's Meta layer.
- It verifies the Kimi-to-Lean machine-checking loop.
- It is not evidence of hard physics theorem-proving ability.
- The heavier physics proof tasks remain defined but currently require local PhysLib/mathlib prebuild completion.

Leakage boundary:
- temp cwd initially contained only `prompt.md`
- gold, verifier, run history, and source metadata were not mounted in cwd
- network was requested off in prompt, but not system-enforced
- agent-created files: `[]`
