# Recommended v0.1 Suite

This is the practical first version to run locally before adding custom frontier tasks.

## Layer 1: Textbook Numeric Baseline

Source:
- SciBench original questions

Target size:
- 24 to 50 questions

Fields:
- classical mechanics
- electromagnetism
- thermodynamics
- waves/optics
- modern physics
- atomic physics
- basic quantum mechanics

Evaluation:
- final numeric answer
- unit-aware tolerances
- preserve original `source` and `problemid`

Why it matters:
- establishes breadth and catches formula/unit failures before we spend effort on frontier tasks

## Layer 2: Competition Reasoning

Source:
- OlympiadBench Physics original questions
- HiPhO text-only subset after extraction

Target size:
- 20 to 40 text-only questions first

Fields:
- mechanics
- electromagnetism
- thermodynamics
- optics
- modern physics

Evaluation:
- final answer where available
- multiple-choice or expression matching where needed

Why it matters:
- tests multi-step modeling under less template-like problem statements

## Layer 3: Undergraduate And General Physics Scaling

Source:
- UGPhysics
- PHYSICS test split
- PHYBench

Target size:
- 50 to 120 problems in the first pass, sampled by domain and difficulty

Fields:
- mechanics
- electromagnetism
- thermodynamics
- optics
- modern physics
- advanced/basic mixed physics depending on source

Evaluation:
- final answer extraction for UGPhysics and PHYSICS
- symbolic partial-credit scoring for PHYBench if EED is reproduced locally

Why it matters:
- this is the fastest way to increase question count without writing custom problems
- it adds more difficult, more recent, and better-metadata physics sources than the current SciBench-only numeric layer

## Layer 4: Condensed Matter And Frontier Physics

Source:
- CMPhysBench
- CMT-Benchmark
- CritPt, once remote grading is acceptable

Current local implementation:
- [existing-open-physics-diverse-v0.1](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/README.md) includes a small CMPhysBench and CMT-Benchmark sample in the default core task.
- [existing-cmt-hard-stress-v0.1](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/README.md) now includes the full 50-row public CMT-Benchmark task as `cmt-hard-research-50`.

Target size:
- 20 to 50 local questions first for CMPhysBench/CMT-Benchmark; CMT-Benchmark is already at 50 local questions
- CritPt kept as a separate remote-graded track

Fields:
- condensed matter physics
- superconductivity
- strongly correlated systems
- magnetism
- semiconductors
- theoretical foundations
- broader modern physics research for CritPt

Evaluation:
- expression or structured answer scoring
- SEED/EED-style partial credit where provided
- remote challenge grading for CritPt

Why it matters:
- this directly fixes the earlier gap where off-the-shelf benchmarks were mostly textbook, olympiad, or generic theory rather than condensed-matter/research physics

## Layer 5: Experiment And Applied Physics

Source:
- OpenXRD
- ThermoQA

Current local implementation:
- [existing-open-physics-diverse-v0.1](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/README.md) includes two ThermoQA real-fluid property questions in the default core task.

Target size:
- 20 to 40 OpenXRD items if license/use boundary is acceptable
- 30 to 60 ThermoQA questions across tiers

Fields:
- crystallography and XRD question answering
- engineering thermodynamics
- real fluids, components, cycles, exergy

Evaluation:
- benchmark-provided evaluation package for OpenXRD
- numeric tolerance and weighted step scoring for ThermoQA

Why it matters:
- it starts covering experimental/materials reasoning and applied thermodynamics, which are almost absent from the existing v0.1 suite

## Layer 6: Graduate/Expert Scientific QA

Source:
- GPQA Physics subset, only if access and usage constraints are acceptable
- TheoremQA physics subset

Target size:
- small, provenance-preserved subset

Fields:
- mixed graduate-level physics and adjacent science

Evaluation:
- multiple-choice exact match

Why it matters:
- checks expert-level domain knowledge and conceptual discrimination

## Layer 7: Frontier Theory

Source:
- TPBench public problems

Target size:
- all publicly accessible physics problems that can be legally and reproducibly used

Current local implementation:
- [existing-tpbench-public-code-v0.1](D:/Playground/agent-lab/benchmarks/existing-tpbench-public-code-v0.1/README.md)

Fields:
- high-energy theory
- general relativity
- cosmology
- mathematical/theoretical physics

Evaluation:
- auto-verifiable answer when provided
- otherwise structured final-answer extraction

Why it matters:
- brings the benchmark closer to real research-level physics, though not yet to the user's condensed-matter focus

## Layer 8: Formal Physics Verification

Source:
- LeanPhysBench benchmark
- PhysLib as supporting Lean4 library

Target size:
- as many public formal statements as can be reproducibly run locally

Fields:
- electromagnetism
- thermodynamics
- modern physics
- mechanics
- waves
- optics

Evaluation:
- Lean4 proof / completion verification
- exact machine-checked success or failure

Why it matters:
- this is the cleanest off-the-shelf path toward verifier-oriented physics-agent evaluation
- unlike result-only tasks, it checks whether the model can operate inside a formal physics language

## Known Gaps For Later Custom Additions

These are not well-covered by currently identified off-the-shelf benchmarks:
- topological order
- topological phases
- oxide thin films
- transport / RHEED / XRD experimental reasoning
- literature-grounded assumption checking

Recommendation:
- do not block v0.1 on these gaps
- add them as a custom frontier/research-agent layer after the off-the-shelf baseline is stable
- strongly correlated condensed matter and superconductivity are now partially covered by CMPhysBench/CMT-Benchmark, but still need custom thesis-aligned additions later
