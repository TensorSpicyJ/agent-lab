# existing-physlib-formal-lane-v0.1

This directory is a seed package for a formal-physics benchmark lane based on PhysLib / LeanPhysBench-style sources.

Current scope:
- a curated shortlist of 20 Lean modules from PhysLib
- declaration-level extraction for those modules
- tooling status notes for local Lean execution
- one runnable `formal-smoke` proof-completion subset
- first three proof-completion task definitions
- precheck note showing the current prebuild blocker after offline dependency repair

This lane now has a small runnable formal-smoke subset. The heavier physics proof tasks remain
defined but currently need local PhysLib/mathlib prebuild completion before they can be scored.

Current local status:
- offline dependency repair was applied to the temporary PhysLib clone used by the verifier
- the verifier now injects the PhysLib repo root into `LEAN_PATH`
- sample verification no longer fails on `git` dependency fetch
- `physlib-meta-smoke-mini-3` is intended to be runnable now
- the heavier physics tasks still report `module_prebuild_required` for target PhysLib modules

Files:
- `manifest.yaml`
- `run-kimi-physlib-formal-smoke.ps1`
- `tasks/...`
- `modules/physlib-formal-shortlist-decls.json`
- `modules/physlib-formal-seed-modules.yaml`
- `TOOLING-STATUS-2026-06-02.md`
- `PRECHECK-2026-06-02.md`

Why this lane matters:
- it moves beyond final-answer checking
- it aligns with verifier-oriented physics-agent evaluation
- it creates a path toward Lean4 machine-checked physics tasks
