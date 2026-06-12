# Existing Open Physics Diverse Benchmark v0.1

This benchmark is a small, locally runnable sample from public/open-data physics benchmark sources. It is designed as a first-pass "diverse physics" score for Kimi Code/Kimi 2.6 before scaling to full datasets.

## Included Sources

- ThermoQA: applied engineering thermodynamics, numeric multi-property answers.
- CMPhysBench: graduate-level theoretical/condensed-matter-adjacent calculation and symbolic answers.
- CMT-Benchmark: research-level condensed matter theory and computational-method reasoning.

## Task

- Default task id: `open-physics-diverse-core-7`
- Hard task id: `open-physics-diverse-mini-8`
- Format: one JSON object with scalar/string/list answers.
- Local grading: exact choice matching, numeric tolerance, and lightweight symbolic normalization.
- Current status: Kimi core run scored at `11/12`, `hard_score = 0.9166666667`.
- Hard stress status: Kimi mini-8 run scored `10/13`, `hard_score = 0.7692307692`, after a `1020.018 s` run.
- Baseline report: [BASELINE-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/BASELINE-2026-06-03.md)

The `mini-8` task includes one additional CMT Hartree-Fock triangular CDW research item. The 2026-06-03 Kimi run completed, but it was much slower than core-7 and missed the added Hartree-Fock item, so `core-7` remains the default score while `mini-8` is kept as a stress track.

## Why This Exists

The earlier local runs already cover SciBench, TPBench public problems, and a PhysLib formal smoke lane. This suite fills a different gap:

- applied thermodynamics
- symbolic graduate physics
- condensed matter theory methods
- research-level multiple-answer reasoning

It is intentionally small and provenance-preserved. The next scale-up step is to automate extraction from the registered full datasets.
