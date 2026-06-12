# Kimi 2.6 Open Physics Scorecard 2026-06-03

## Conclusion

Across the currently materialized open/public physics benchmark lanes, Kimi 2.6 scores `30/32 = 0.9375` by local answer-check count.

This is a local mixed-harness scorecard, not one official benchmark number. The included lanes use different grading modes: result-only numeric checks, executable code checks, formal smoke verification, and a mixed open-data verifier.

After expanding the research-level CMT hard lane to the full public 50-row CMT-Benchmark task, Kimi scores `0/50` on that stress lane.

## Included Local Scores

| Local benchmark | Domain role | Grading mode | Kimi result |
| --- | --- | --- | ---: |
| `existing-scibench-physics-result-only-v0.1` | broad textbook physics | result-only numeric | `7/8` |
| `existing-tpbench-public-code-v0.1` | public theoretical physics examples | executable Python answer functions | `9/9` |
| `existing-physlib-formal-lane-v0.1` | formal physics smoke lane | Lean/proof-oriented local checks | `3/3` |
| `existing-open-physics-diverse-v0.1` | ThermoQA + CMPhysBench + CMT-Benchmark sample | numeric, symbolic, choice-set | `11/12` |
| Total | mixed open/public physics baseline | local answer-check aggregate | `30/32` |

## Hard Replacement Suite

| Local benchmark | Domain role | Grading mode | Kimi result |
| --- | --- | --- | ---: |
| `existing-cmt-hard-stress-v0.1::cmt-hard-research-50` | research-level CMT stress lane | choice-set, vector, symbolic, no-output failure scoring | `0/50` |
| `existing-cmt-hard-stress-v0.1::cmt-hard-research-8` | compact CMT regression slice | choice-set, vector, symbolic, no-output failure scoring | `0/8` |

The full CMT50 task uses all 50 public CMT-Benchmark rows. Itemwise execution with a `45 s` per-item timeout produced 49 timeouts and one completed but incorrect answer, for `0/50` in `2229.822 s`. The compact 8-item slice remains as a same-size comparison against `open-physics-diverse-mini-8`.

## Coverage Gained

The current materialized suite now covers:

- classical mechanics and orbital mechanics
- modern, atomic, and basic quantum physics
- statistical mechanics and blackbody scaling
- public theoretical-physics code-answer tasks
- formal physics proof smoke tasks
- engineering thermodynamics and real-fluid property lookup
- graduate symbolic quantum/theoretical-foundation questions
- condensed matter theory methods: Hubbard symmetries, DMRG scaling, and QMC average sign

## Stress Track

The hard `open-physics-diverse-mini-8` task added a CMT Hartree-Fock triangular charge-density-wave item. Kimi completed the run after `1020.018 s` and scored `10/13`, `hard_score = 0.7692307692`, so it is recorded separately as a stress-track degradation rather than folded into the core aggregate.

The newer `existing-cmt-hard-stress-v0.1` suite is the more useful hard stress layer: the full CMT50 task gives `0/50` and has enough failures to diagnose Kimi's research-level condensed-matter limits.

## Source Inventory

The catalog now tracks 19 external open or benchmark-relevant physics sources plus the local diverse aggregate lane. The most important next extraction targets are UGPhysics, HiPhO, PHYSICS, PHYBench, CMPhysBench, CMT-Benchmark, OpenXRD, and ThermoQA.

Primary source pages used for the new diverse lane:

- ThermoQA: https://huggingface.co/datasets/olivenet/thermoqa
- CMPhysBench: https://huggingface.co/datasets/weidawang/CMPhysBench
- CMT-Benchmark: https://huggingface.co/datasets/JVRoggeveen/cmt_benchmark

## Interpretation Boundary

The `30/32` number is useful as a local Kimi baseline for this repo. It should not be reported as an official SciBench, TPBench, LeanPhysBench, ThermoQA, CMPhysBench, or CMT-Benchmark leaderboard result.
