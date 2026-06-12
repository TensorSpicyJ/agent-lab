# Source Notes

## SciBench

Link:
- [xw27/scibench on Hugging Face](https://huggingface.co/datasets/xw27/scibench)

Local use:
- A small original-question subset is already implemented in [existing-scibench-physics-result-only-v0.1](D:/Playground/agent-lab/benchmarks/existing-scibench-physics-result-only-v0.1/README.md).

Notes:
- Good fit for result-only numeric grading.
- Direct Hugging Face file download was unreliable from this machine, so the current subset was copied from public dataset pages rather than mirrored wholesale.

## OlympiadBench

Link:
- [lscpku/OlympiadBench-official on Hugging Face](https://huggingface.co/datasets/lscpku/OlympiadBench-official)

Candidate use:
- Add a text-only English physics subset after reliable data access is confirmed.

Notes:
- Need to filter out image-dependent entries unless we add multimodal handling.

## GPQA

Link:
- [GPQA paper](https://arxiv.org/abs/2311.12022)

Candidate use:
- Use only if local access and redistribution constraints are acceptable.

Notes:
- Treat as access/policy-sensitive.
- Best for multiple-choice expert QA rather than numeric result-only physics.

## TPBench

Links:
- [TPBench website](https://tpbench.org/)
- [TPBench paper](https://arxiv.org/abs/2502.15815)
- [ZhiqiGao/TPBench on Hugging Face](https://huggingface.co/datasets/ZhiqiGao/TPBench)

Candidate use:
- Public problems have started to be added as a frontier-theory layer in [existing-tpbench-public-code-v0.1](D:/Playground/agent-lab/benchmarks/existing-tpbench-public-code-v0.1/README.md).

Notes:
- Complete data is intentionally restricted to reduce benchmark leakage.
- Stronger match to high-energy theory, cosmology, and general relativity than to condensed matter or superconductivity.

## LeanPhysBench / PhysLib

Links:
- [PhysLib website](https://physlib.io/)
- [Lean4Physics paper / OpenReview](https://openreview.net/forum?id=qRLOQ2U4Ea)
- [PhysLean repository](https://github.com/HEPLean/PhysLean)
- [leanprover-community/physlib](https://github.com/leanprover-community/physlib)

Candidate use:
- Add a formal-physics benchmark lane with Lean4 verification.

Notes:
- `PhysLib` is the Lean4 physics library, not the benchmark itself.
- `LeanPhysBench` is reported as a 200-statement formal benchmark spanning several standard college-physics domains.
- This lane is format-wise different from result-only numeric grading and TPBench-style code answers.
- Local inspection on 2026-06-02 confirmed repository access via `HEPLean/PhysLean`, whose README states the project was renamed/moved to `leanprover-community/physlib`.
- Local repository scan counted `444` `Physlib/*.lean` files and `84` `QuantumInfo/*.lean` files.

## 2026-06-03 Open/Public Candidate Expansion

Detailed scan:
- [open-source-candidate-scan-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-physics-benchmarks-catalog-v0.1/open-source-candidate-scan-2026-06-03.md)

Local materialization:
- [existing-open-physics-diverse-v0.1](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/README.md) is a small local verifier sample from ThermoQA, CMPhysBench, and CMT-Benchmark.
- Kimi 2.6 baseline: `11/12`, `hard_score = 0.9166666667`; see [BASELINE-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/BASELINE-2026-06-03.md).
- [existing-cmt-hard-stress-v0.1](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/README.md) now contains the full 50-row CMT-Benchmark hard stress task plus a compact 8-item slice.
- Kimi 2.6 full CMT50 hard stress baseline: `0/50`, `hard_score = 0.0`; see [BASELINE-CMT50-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/BASELINE-CMT50-2026-06-03.md).
- Kimi 2.6 compact CMT8 hard stress baseline: `0/8`, `hard_score = 0.0`; see [BASELINE-2026-06-03.md](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/BASELINE-2026-06-03.md).

High-priority physics-specific sources:
- [UGPhysics](https://github.com/YangLabHKUST/UGPhysics): undergraduate physics benchmark with public Hugging Face dataset.
- [HiPhO](https://github.com/SciYu/HiPhO): recent high-school physics olympiad benchmark with answer-level and step-level scoring.
- [PHYSICS](https://github.com/Zhengsh123/PHYSICS): large open-ended physics reasoning dataset with domain, difficulty, answer, and answer-type metadata.
- [PHYBench](https://github.com/phybench-official/phybench): symbolic physics reasoning benchmark with Expression Edit Distance scoring.
- [CMPhysBench](https://github.com/CMPhysBench/CMPhysBench): condensed-matter physics benchmark with superconductivity, magnetism, strongly correlated systems, semiconductors, and theoretical foundations.
- [CMT-Benchmark](https://huggingface.co/datasets/JVRoggeveen/cmt_benchmark): expert research-level condensed matter theory problems.
- [CritPt](https://github.com/CritPt-Benchmark/CritPt): frontier physics research challenges with remote grading.

Experiment/applied sources:
- [OpenXRD](https://github.com/niaz60/OpenXRD): XRD and crystallography QA benchmark; evaluation-only and noncommercial boundary.
- [ThermoQA](https://huggingface.co/datasets/olivenet/thermoqa): applied engineering thermodynamics benchmark with CoolProp-grounded answers.
- [PhysUniBench](https://github.com/PrismaX-Team/PhysUniBenchmark): undergraduate multimodal physics benchmark candidate; schema still needs verification.

Reference baselines:
- [MMLU](https://github.com/hendrycks/test): high-school and college physics multiple-choice baseline.
- [C-Eval](https://github.com/hkust-nlp/ceval): Chinese high-school and college physics multiple-choice baseline.
- [AGIEval](https://github.com/ruixiangcui/AGIEval): includes Gaokao Physics in the public exam benchmark.
- [TheoremQA](https://github.com/TIGER-AI-Lab/TheoremQA): theorem-driven STEM QA with a physics subset.

Use boundaries:
- Do not copy larger source subsets into local benchmark folders until each source's license, split policy, and original redistribution boundary are checked.
- For PHYSICS, use the held-out test split for model evaluation; do not mix training examples with generated reasoning paths into the benchmark score.
- For mixed-modal sources such as HiPhO and PhysUniBench, extract text-only subsets first and register figure-dependent entries separately.
- For OpenXRD, keep its evaluation-only restriction explicit and do not use it for training, fine-tuning, distillation, or alignment.
- For CritPt, treat local runs as generation-only unless official remote grading is used.
