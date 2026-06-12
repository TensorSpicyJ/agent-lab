# Open-Source Candidate Scan 2026-06-03

Scope note:
- "Open-source/open-data" here means the project exposes a public repository, a public Hugging Face dataset, or a public downloadable data package.
- This does not automatically mean unrestricted redistribution. Each entry still needs a final license/provenance check before copying original questions into local benchmark folders.
- Status labels below are for our local benchmark pipeline, not claims about the original project's official maturity.

## High-Priority Physics-Specific Sources

| Source | Confirmed public entry point | Local status | Physics scope | Problem/task type | Answer/evaluation style | Size signal | Why it matters | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| UGPhysics | https://github.com/YangLabHKUST/UGPhysics and https://huggingface.co/datasets/UGPhysics/ugphysics | registered_candidate_pending_download | undergraduate physics; 3 main domains, 13 core subjects, 59 topics | open physics problem solving | final answer in boxed format; repo has inference/eval scripts | 5,520 problems | Best broad undergraduate layer after SciBench; much larger and more structured | Download and license need final local check before materialization |
| HiPhO | https://github.com/SciYu/HiPhO and https://huggingface.co/datasets/SciYu/HiPhO | registered_candidate_pending_multimodal_filter | high-school physics olympiads; mechanics, electromagnetism, thermodynamics, optics, modern physics | olympiad exam problems, including text-only and figure-based items | official marking schemes; answer-level and step-level scoring | 13 olympiads, 360 problems | Hard current competition layer; stronger than generic textbook tasks | Mixed-modal data; extract text-only subset first |
| PHYSICS | https://github.com/Zhengsh123/PHYSICS and https://huggingface.co/datasets/desimfj/PHYSICS | registered_candidate_pending_download | mechanics, electromagnetism, thermodynamics, optics, modern physics; high school through undergraduate/graduate | open-ended physics problems with solutions and answers | Rule+Model assessment; answer types include interval, expression, equation, true/false, MCQ, numerical, open-ended | 16,568 total; 14,568 train and 2,000 test | Large-scale general physics reasoning layer with topic/difficulty metadata | Use test split only for benchmarking; training split includes model-generated reasoning paths |
| PHYBench | https://github.com/phybench-official/phybench and https://huggingface.co/datasets/Eureka-Lab/PHYBench | registered_candidate_pending_download | mechanics, electromagnetism, thermodynamics, optics, modern physics, advanced physics | original symbolic physics problems | Expression Edit Distance (EED) partial-credit metric | 500 problems; 100 fully detailed plus 400 additional examples | Good symbolic-expression reasoning benchmark; text-only by design | Need inspect released HF data fields before local harness |
| CMPhysBench | https://github.com/CMPhysBench/CMPhysBench and https://huggingface.co/datasets/weidawang/CMPhysBench | registered_candidate_high_priority_frontier | condensed matter physics: magnetism, superconductivity, strongly correlated systems, semiconductors, theoretical foundations | graduate-level calculation problems | Scalable Expression Edit Distance (SEED) partial credit | 520 problems | Directly fills the condensed-matter/superconductivity gap in the current catalog | Need extract answer schema and reproduce SEED scorer locally |
| CMT-Benchmark | https://huggingface.co/datasets/JVRoggeveen/cmt_benchmark and https://github.com/JamesRoggeveen/cmt_benchmark_data | registered_candidate_high_priority_frontier | condensed matter theory; ED, statistical mechanics, QMC, Hartree-Fock, DMRG, PEPS, VMC, other methods | expert-authored research-level problems | pass/fail or structured evaluation through provided code | 50 original problems | Small but very frontier-aligned for theoretical condensed matter | License/provenance should be checked at data-file level before copying |
| CritPt | https://github.com/CritPt-Benchmark/CritPt and https://huggingface.co/datasets/CritPt-Benchmark/CritPt | registered_candidate_remote_grading | unpublished frontier physics research across condensed matter, quantum, AMO, astrophysics, statistical, nuclear, HEP, mathematical physics, fluids, nonlinear dynamics, biophysics | multi-checkpoint research challenges | official remote grading server; challenge accuracy | 71 challenges and 190 checkpoints; 70 public test challenges | Closest open source found to genuine research-agent physics evaluation | Grading is server mediated; local offline scoring may be incomplete |

## Experiment, Engineering, and Multimodal Physics Sources

| Source | Confirmed public entry point | Local status | Physics scope | Problem/task type | Answer/evaluation style | Size signal | Why it matters | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenXRD | https://github.com/niaz60/OpenXRD | registered_candidate_experimental_xrd | crystallography and XRD question answering | LLM/MLLM XRD QA | closedbook/openbook-style evaluation package | public repo includes zipped evaluation dataset | Directly relevant to XRD/experimental-analysis benchmark layer | Evaluation-only, noncommercial license; do not use for training or fine-tuning |
| ThermoQA | https://huggingface.co/datasets/olivenet/thermoqa | registered_candidate_applied_thermo | engineering thermodynamics; real fluids, components, cycles, exergy | open calculation questions | numeric tolerance and weighted step-level scoring grounded in CoolProp | 293 questions across 3 tiers | Good applied thermo layer beyond textbook formula recall | Community dataset; verify GitHub/code package and licenses before relying on it |
| PhysUniBench | https://github.com/PrismaX-Team/PhysUniBenchmark | registered_candidate_multimodal_undergrad | undergraduate physics | diagram-paired QA and MCQ | pending extraction | repo confirmed; size not confirmed from README snapshot | Useful for vision-plus-symbolic undergraduate reasoning | Data availability and exact schema need verification |

## General Exam/Theorem Baselines With Physics Subsets

| Source | Confirmed public entry point | Local status | Physics scope | Problem/task type | Answer/evaluation style | Size signal | Why it matters | Caveats |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| MMLU Physics | https://github.com/hendrycks/test | registered_candidate_baseline_mcq | high school physics and college physics subjects | multiple-choice questions | exact option match | MMLU has 57 total tasks | Cheap common baseline for comparability with prior LLM results | Not hard enough for frontier physics; only use as a reference layer |
| C-Eval Physics | https://github.com/hkust-nlp/ceval and https://huggingface.co/datasets/ceval/ceval-exam | registered_candidate_chinese_mcq | Chinese high school physics and college physics; also part of C-Eval Hard | multiple-choice questions | exact option match; validation labels public, test labels via submission | 13,948 questions across 52 disciplines | Chinese physics baseline; useful for Kimi-style Chinese reasoning | Dataset license is CC BY-NC-SA 4.0; preserve split boundaries |
| AGIEval Gaokao Physics | https://github.com/ruixiangcui/AGIEval | registered_candidate_exam_mcq | Chinese Gaokao physics | official exam-style MCQ | exact option match | AGIEval v1.1 has 20 tasks | Public exam baseline; more realistic than generic MCQ | Original exam dataset license/provenance must be respected |
| TheoremQA Physics | https://github.com/TIGER-AI-Lab/TheoremQA and https://huggingface.co/datasets/TIGER-Lab/TheoremQA | registered_candidate_theorem_qa | theorem-driven STEM QA including physics | university-level theorem application QA | short answer; WolframAlpha-assisted evaluation in original pipeline | 800 QA pairs across 350+ theorems | Tests theorem selection and application rather than routine calculation | Need filter physics subset and inspect answer format |

## Not Registered Yet

These names appeared in search or prior discussion, but need a stronger public source confirmation before adding to the machine-readable catalog:
- JEEBench: likely useful for IIT-JEE physics, but no stable official source was confirmed in this scan.
- SciCode physics tasks: likely useful for scientific coding, but physics-specific task coverage was not confirmed in this scan.
- Theoria / GravityBench / SeePhys style sources: keep as watchlist until data schema and physics relevance are verified.

## Recommended Extraction Order

1. CMPhysBench and CMT-Benchmark: highest value for condensed matter, superconductivity, and research-level theory.
2. UGPhysics, PHYSICS, PHYBench, and HiPhO text-only subset: strongest broad physics scaling layer.
3. OpenXRD and ThermoQA: experimental/materials and applied-thermo lanes that the current suite lacks.
4. C-Eval, AGIEval, MMLU, and TheoremQA physics subsets: cheap multiple-choice/theorem baselines for comparability.
5. CritPt: keep as a frontier research-agent track once remote grading workflow is acceptable.
