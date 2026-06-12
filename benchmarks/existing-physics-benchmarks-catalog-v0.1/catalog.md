# Catalog

## Tier A: Direct Local Use Now

### SciBench

- Status: direct local subset already implemented
- Local benchmark: [existing-scibench-physics-result-only-v0.1](D:/Playground/agent-lab/benchmarks/existing-scibench-physics-result-only-v0.1/README.md)
- Source format: text problems with numeric answers and units
- Local grading style: result-only numeric verification
- Physics level: undergraduate to early graduate textbook physics
- Current local result: `7/8`, `hard_score = 0.8750`

Fields currently represented locally:
- classical mechanics
- modern physics
- atomic physics
- basic quantum mechanics
- thermal/de Broglie matter-wave calculation

Best use:
- broad physics arithmetic/modeling baseline
- unit-handling and formula-selection checks
- scalable result-only testing

Limit:
- not frontier research
- many questions remain textbook-style

### TPBench Public Problems

- Status: direct local public mini-suite implemented
- Local benchmark: [existing-tpbench-public-code-v0.1](D:/Playground/agent-lab/benchmarks/existing-tpbench-public-code-v0.1/README.md)
- Source format: public theoretical physics problems with Python-code answer requirements
- Local grading style: executable answer functions on hidden numerical checks
- Physics level: theoretical physics, from easy public examples upward
- Current local result: `9/9`, `hard_score = 1.0000`

Fields currently represented locally:
- blackbody dimensional scaling
- orbital/escape mechanics
- basic quantum-mechanics expectation value

Best use:
- code-answer harness for public TPBench problems
- first step toward frontier-theory stress testing

Limit:
- current public mini-suite is small
- complete TPBench is intentionally restricted to reduce leakage

### LeanPhysBench + PhysLib

- Status: benchmark registered, PhysLib repo access confirmed
- Benchmark/library relation:
  - `LeanPhysBench` is the benchmark
  - `PhysLib` is the supporting Lean4 physics library, not the benchmark itself
- Source format: Lean4 formal theorem statements plus machine verification
- Physics level: college-level formal physics reasoning
- Reported size: 200 manually crafted and peer-reviewed statements
- Local repository signal:
  - official codebase accessible via the renamed `PhysLean` repository path
  - local repo scan found `444` Lean files under `Physlib/` and `84` under `QuantumInfo/`

Fields reported in the paper:
- electromagnetism
- thermodynamics
- modern physics
- mechanics
- waves
- optics

Best use:
- benchmarking formal physics reasoning rather than just final-answer correctness
- evaluating whether a model can translate or complete verifiable physics statements in Lean4
- strong match to the user's long-term verifier-oriented physics-agent direction
- corpus-scale source for later benchmark/task extraction in mechanics, EM, QM, relativity, QFT, and condensed matter

Limit:
- different task format from current result-only and code-answer suites
- requires Lean4-based verification harness
- adding `PhysLib` alone does not increase benchmark question count; the quantity comes from `LeanPhysBench`

### Open Physics Diverse Core

- Status: direct local mixed-source mini-suite implemented
- Local benchmark: [existing-open-physics-diverse-v0.1](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/README.md)
- Source format: public/open-data questions sampled from ThermoQA, CMPhysBench, and CMT-Benchmark
- Local grading style: numeric tolerance, symbolic normalization, and exact choice-set matching
- Physics level: engineering thermodynamics through graduate symbolic physics and research-level CMT methods
- Current local result: `11/12`, `hard_score = 0.9167`
- Baseline note: [BASELINE-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/BASELINE-2026-06-03.md)

Fields currently represented locally:
- engineering thermodynamics
- quantum mechanics theoretical foundations
- condensed matter theory methods
- statistical mechanics methods

Best use:
- filling gaps left by SciBench, TPBench public, and PhysLib smoke tasks
- first compact Kimi baseline over open/public applied, symbolic, and CMT sources
- preserving a reproducible path from source benchmark to local verifier

Limit:
- small manually sampled subset, not a full official benchmark run
- `open-physics-diverse-mini-8` is much slower and scored lower on Kimi: `10/13`, `hard_score = 0.7692`

### CMT Hard Stress

- Status: direct local hard stress suite implemented
- Local benchmark: [existing-cmt-hard-stress-v0.1](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/README.md)
- Source format: public CMT-Benchmark research-level questions with answer keys
- Local grading style: exact choice-set matching, numeric-vector tolerance, symbolic normalization, and structured no-output failure scoring
- Physics level: research-level condensed matter theory
- Current full local result: `0/50`, `hard_score = 0.0000`
- Full baseline note: [BASELINE-CMT50-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/BASELINE-CMT50-2026-06-03.md)
- Compact 8-item baseline note: [BASELINE-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/BASELINE-2026-06-03.md)

Fields currently represented locally:
- variational Monte Carlo
- fractional quantum Hall exact diagonalization
- Hubbard model exact diagonalization and particle-hole transformations
- determinant quantum Monte Carlo sign-problem criteria
- strongly correlated boson transport

Best use:
- full 50-question hard stress task for the requested CMT-Benchmark target
- compact same-size replacement for the previous too-easy 8-problem suite
- compact failure-rich stress test for Kimi
- diagnosing long-reasoning/no-final-answer behavior on research-level CMT

Limit:
- intentionally not balanced for general physics breadth
- current Kimi result is dominated by timeout/no-final-answer behavior, not fine-grained partial correctness

### OlympiadBench Physics

- Status: registered, not yet locally extracted because direct Hugging Face data download timed out from this machine
- Source format: competition-style problems; some subsets include text-only physics
- Candidate subset: English physics competition questions
- Physics level: olympiad/high-school competition to undergraduate-style reasoning

Likely fields:
- classical mechanics
- electromagnetism
- thermodynamics
- optics
- waves
- modern physics

Best use:
- harder multi-step physics word problems
- robust benchmark breadth outside standard textbook examples

Limit:
- may require dataset download reliability and subset filtering
- some entries may be multimodal or require figure handling

## Tier B: Open Candidate Extraction Next

These sources were added from the 2026-06-03 open-source scan. They are not yet copied into local task folders, but each has a confirmed public repository, dataset page, or downloadable package.

Detailed scan:
- [open-source-candidate-scan-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-physics-benchmarks-catalog-v0.1/open-source-candidate-scan-2026-06-03.md)

### UGPhysics

- Status: registered candidate, pending download and license/provenance check
- Source format: undergraduate physics problem dataset plus inference/evaluation scripts
- Reported size: 5,520 problems across 3 main domains, 13 core subjects, and 59 topics
- Physics level: undergraduate physics

Best use:
- broad undergraduate layer between SciBench and frontier theory
- large-scale domain/topic balanced sampling

Limit:
- needs local dataset download
- final answer schema and license need local verification before copying questions

### HiPhO

- Status: registered candidate, pending text-only extraction and multimodal filtering
- Source format: recent real-world physics olympiad papers with annotations
- Reported size: 13 olympiads and 360 problems
- Physics fields: mechanics, electromagnetism, thermodynamics, optics, modern physics

Best use:
- hard competition reasoning
- step-level grading where official marking schemes are available

Limit:
- mixed-modal items require figure handling
- first local pass should filter text-only problems

### PHYSICS

- Status: registered candidate, pending download
- Source format: large open-ended physics problem dataset with answers, solutions, domain, difficulty, and answer-type metadata
- Reported size: 16,568 total samples, including a 2,000-sample test split
- Physics fields: mechanics, electromagnetism, thermodynamics, optics, modern physics

Best use:
- large-scale result-answer and open-answer physics reasoning layer
- difficulty-stratified evaluation from high school through undergraduate/graduate physics

Limit:
- training split includes generated reasoning paths; benchmark extraction should use the held-out test split

### PHYBench

- Status: registered candidate, pending data-field inspection
- Source format: original symbolic physics problems plus EED metric implementation
- Reported size: 500 problems
- Physics fields: mechanics, electromagnetism, thermodynamics, optics, modern physics, advanced physics

Best use:
- symbolic expression-answer grading with partial credit
- robust reasoning and physical-perception error analysis

Limit:
- need inspect public Hugging Face files and reproduce the Expression Edit Distance scorer

### CMPhysBench

- Status: high-priority frontier candidate
- Source format: graduate-level condensed-matter calculation problems
- Reported size: 520 problems
- Physics fields: magnetism, superconductivity, strongly correlated systems, semiconductors, theoretical foundations

Best use:
- strongest open candidate found so far for condensed-matter and superconductivity coverage
- natural bridge from generic physics benchmarks to the user's research-adjacent interests

Limit:
- local harness should reproduce or wrap the SEED scorer before running model baselines

### CMT-Benchmark

- Status: included through the local full CMT50 hard stress lane
- Source format: expert-authored research-level condensed matter theory problems
- Reported size: 50 original problems
- Physics/method fields: exact diagonalization, statistical mechanics, quantum Monte Carlo, Hartree-Fock, DMRG, PEPS, VMC, and other CMT methods

Best use:
- small but hard research-agent layer for condensed matter theory

Limit:
- local CMT50 uses deterministic answer-key checking; it is still not an official leaderboard submission

### OpenXRD

- Status: registered experimental-analysis candidate
- Source format: repo-first XRD question-answering benchmark with zipped public evaluation dataset
- Physics/materials field: crystallography and XRD reasoning

Best use:
- first off-the-shelf experimental/materials-characterization layer
- relevant to XRD reasoning beyond textbook physics

Limit:
- evaluation-only and noncommercial use boundary
- not for model training, fine-tuning, distillation, or alignment

### ThermoQA

- Status: registered applied-thermodynamics candidate
- Source format: Hugging Face dataset with question JSONL tiers
- Reported size: 293 questions
- Physics field: engineering thermodynamics, real-fluid property lookup, components, cycles, exergy

Best use:
- numeric and step-level applied thermodynamics
- tool-use comparison because ground truth is tied to CoolProp

Limit:
- community benchmark; verify package/source and license before treating it as a canonical public benchmark

### CritPt

- Status: registered frontier candidate with remote grading
- Source format: public challenge data plus official grading server
- Reported size: 71 challenges and 190 checkpoints
- Physics fields: condensed matter, quantum physics, AMO, astrophysics, statistical physics, nuclear physics, high-energy physics, mathematical physics, fluid dynamics, nonlinear dynamics, biophysics

Best use:
- closest found source for genuine frontier physics research reasoning
- useful for tool-augmented research-agent evaluation

Limit:
- local offline grading is incomplete unless the official server is used
- submissions are batch-limited

### Exam/Theorem Physics Subsets

Registered as baseline/comparability layers:
- MMLU high school physics and college physics: common English MCQ baseline
- C-Eval high school physics and college physics: Chinese MCQ baseline and C-Eval Hard component
- AGIEval Gaokao Physics: official exam-style Chinese MCQ baseline
- TheoremQA Physics subset: theorem-driven university-level QA

Best use:
- cheap baselines for broad model comparison
- not the main hard physics benchmark layer

Limit:
- mostly multiple-choice or short-answer
- not enough for frontier physical reasoning by themselves

## Tier C: Useful, But Needs Access Or Policy Handling

### GPQA Physics

- Status: useful but access/policy-sensitive
- Source format: multiple-choice expert questions
- Physics level: graduate-level, Google-proof scientific QA
- Best use: hard conceptual and domain-knowledge checks

Fields likely covered:
- advanced physics across mixed subfields
- interdisciplinary science questions

Limit:
- dataset access and redistribution must be handled carefully
- not necessarily numeric result-only
- many questions are multiple-choice rather than derivation/proof tasks

### TPBench Full / Non-Public Set

- Status: high-value frontier-theory target; partial public access only
- Source format: theoretical physics problems with auto-verifiable answers
- Physics level: undergraduate through frontier research

Fields explicitly relevant:
- high-energy theory
- cosmology
- general relativity
- mathematical/theoretical physics

Best use:
- frontier-theory stress testing
- reasoning under advanced formalism
- auto-verifiable research-level target where public questions are available

Limit:
- complete set is not openly exposed to avoid leakage
- field distribution is not aligned with condensed matter / superconductivity by default

## Tier D: Useful Reference, But Not The Core Local v0.1

### PhyBench / PhysicsBench-style datasets

- Status: candidate research target
- Use only after confirming source availability, license, and answer format
- Best use: broader physics reasoning comparisons if the dataset exposes enough answer metadata

### Textbook/OpenStax Problems

- Status: already tested as public-source suites, but not off-the-shelf benchmark datasets
- Local benchmark examples:
  - [web-physics-result-only-v0.1](D:/Playground/agent-lab/benchmarks/web-physics-result-only-v0.1/README.md)
  - [web-physics-hard-result-only-v0.1](D:/Playground/agent-lab/benchmarks/web-physics-hard-result-only-v0.1/README.md)
  - [web-physics-adversarial-result-only-v0.1](D:/Playground/agent-lab/benchmarks/web-physics-adversarial-result-only-v0.1/README.md)

Best use:
- sanity checks and custom probe construction

Limit:
- not counted as "existing benchmark original questions"
