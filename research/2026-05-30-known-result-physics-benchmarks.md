# Known-Result Physics Benchmarks for Research Agents

Date: 2026-05-30

## Short Conclusion

The closest existing line to "run benchmarks on known physics results" is not generic physics QA. It is paper/result reproduction:

- reproduce a known derivation from a research paper;
- reproduce a known computational result with code;
- reconstruct a known research workflow from curated papers;
- compare final symbolic/numeric answers against machine-checkable ground truth.

This is a better starting point for our research agent than frontier discovery benchmarks.

## Relevant Existing Work

| Work | What it tests | Why it matters for us |
| --- | --- | --- |
| Quantum Many-Body Physics Calculations with LLMs | Hartree-Fock derivations from 15 quantum many-body papers | Closest template for "known result -> structured derivation benchmark" in condensed matter |
| CURIE | Long-context scientific tasks from research documents, including theoretical condensed matter physics and Hartree-Fock derivation tasks | Useful for paper-grounded workflows and ground-truth response files |
| SciCode | Scientific code generation from real research problems, with gold solutions and tests | Good template for code/numerical reproduction tasks |
| CMT-Benchmark | 50 expert-designed condensed matter theory problems with programmatic grading | Strong reference for CMT-specific symbolic/computational grading |
| TPBench | Theoretical physics problems with auto-verifiable answers | Useful grading/harness reference, but less paper-reproduction oriented |
| CritPt | Frontier physics research-style problems with checkpoint tasks and machine-verifiable answers | Too hard for our first benchmark, but valuable as an aspirational stress test |
| PRL-Bench | End-to-end physics research workflows from 100 PRL papers | Very close in spirit, but probably too large/high-level for first local loop |

## Recommended Local First Slice

Start with 5-10 known-result tasks, not a public leaderboard:

1. Hartree-Fock style derivation from a known condensed-matter paper.
2. Toric code GSD=4 proof/check in our local Lean/theory line.
3. A known LSCO/oxide paper claim extraction task with source grounding.
4. A sample XRD/transport analysis task where we already trust the human conclusion.
5. A simple numerical reproduction task with reference output and tolerance.

Each task should store:

- `input.md`: what the agent sees;
- `gold.md` or `gold.json`: expected result;
- `rubric.yaml`: checks such as source grounding, formula equivalence, assumptions, units, limits;
- `verify.py`: mechanical checks where possible;
- `notes.md`: why the known result is safe to use as ground truth.

## Design Implication

Benchmark the agent's reliability on reconstructing known science before asking whether it can discover new science.

The first useful score is not "new discovery". It is:

- did it recover the right result;
- did it preserve assumptions;
- did it cite the right source;
- did it pass physical sanity checks;
- did it avoid overclaiming when evidence was missing.

## Scoring Patterns Worth Reusing

| Source | Scoring style | Reusable lesson |
| --- | --- | --- |
| Quantum many-body / Hartree-Fock | Human expert scores each derivation response across Adherence, Rigor, Knowledge, and Correctness; categorical 0 / 50 / 100 per layer | Best template for our derivation benchmark. It separates "followed instructions" from "math correct" and "physics sensible". |
| CURIE | Mixed metrics: ROUGE-L / BERTScore for long text, IoU for map boxes, identity ratio for protein sequences, LLMSim F1 for structured dict outputs, plus expert good/ok/bad ratings | Useful when outputs are heterogeneous. Do not force one metric across all scientific tasks. |
| SciCode | Pass/fail test suites for subproblems and main problems; numerical input-output tests plus domain-specific tests from papers or analytical solutions | Best template for numerical/code reproduction. It gives clean automation and exposes error accumulation across substeps. |
| CMT-Benchmark | Programmatic exact checking against expert ground truth; symbolic grading for algebraic answers and non-commuting operator expressions using normal ordering | Best template for exact-answer CMT tasks, but too strict for early paper-reading/derivation tasks. |
| TPBench | Auto-verifiable answer checks plus holistic grading for reasoning quality | Good reminder to keep final-answer checks separate from process-quality checks. |
| CritPt | Composite research challenges decomposed into checkpoint tasks with guess-resistant, machine-verifiable answers | Useful aspirational design: split hard research tasks into smaller checkpoint tasks. |
| PRL-Bench | End-to-end workflow score from PRL-paper-derived research tasks, emphasizing objective verifiability | Good later-stage benchmark once our agent can already pass smaller known-result tasks. |

## Suggested Scoring Table for Our First Local Benchmark

Use a hybrid rubric rather than a single accuracy number:

| Dimension | Score | Judge |
| --- | --- | --- |
| final_result | 0 / 0.5 / 1 | mechanical when possible, otherwise expert |
| derivation_validity | 0 / 0.5 / 1 | expert or structured LLM judge with spot checks |
| assumptions_preserved | 0 / 0.5 / 1 | rubric / expert |
| physics_checks | 0 / 0.5 / 1 | mechanical checks: dimension, limit, symmetry, Hermiticity |
| source_grounding | 0 / 0.5 / 1 | script + human review |
| uncertainty_control | 0 / 0.5 / 1 | rubric / human review |

Suggested aggregate:

```text
score = 0.30 final_result
      + 0.20 derivation_validity
      + 0.15 assumptions_preserved
      + 0.15 physics_checks
      + 0.10 source_grounding
      + 0.10 uncertainty_control
```

For early development, keep the per-dimension scores more important than the aggregate score.

## Source Pointers

- `https://arxiv.org/abs/2403.03154`
- `https://arxiv.org/abs/2503.13517`
- `https://github.com/google/curie`
- `https://arxiv.org/abs/2407.13168`
- `https://arxiv.org/abs/2510.05228`
- `https://tpbench.org/`
- `https://arxiv.org/abs/2502.15815`
- `https://arxiv.org/abs/2509.26574`
- `https://arxiv.org/abs/2604.15411`
