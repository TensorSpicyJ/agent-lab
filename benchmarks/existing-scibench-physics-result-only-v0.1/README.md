# existing-scibench-physics-result-only-v0.1

This benchmark uses original physics problems copied from the public `xw27/scibench` dataset page on Hugging Face, preserving the original `source` and `problemid` fields for traceability.

Scope:
- `class_sol.json`
- `matter_sol.json`
- `quan_sol.json`

Design:
- result-only evaluation
- final numeric answer only
- no derivation grading
- original benchmark problem statements, not self-authored variants

Current suite:
- `scibench-physics-mixed-8`
- per-problem attributes in `tasks/scibench-physics-mixed-8/problem-metadata.yaml`

Important boundary:
- This is a small directly copied subset for local evaluation convenience, not a full mirror of SciBench.
