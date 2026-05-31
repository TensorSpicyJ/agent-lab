# Derivation Benchmark Comparison

Date: 2026-05-30

## Short Conclusion

`toric-code-gsd-basic` is a derivation-heavy smoke task. It should not be treated
as equivalent to mature derivation benchmarks such as Hartree-Fock paper
reproduction, CMT-Benchmark, or TPBench.

Its value is now split into two layers: a machine-verified `hard_score` for
agent comparison, and a diagnostic rubric for explaining failures. Its weakness
is that it is still too familiar and not paper-grounded.

## Comparison

| Benchmark | Task form | Rubric / grading form | Main purpose |
| --- | --- | --- | --- |
| Quantum many-body Hartree-Fock benchmark | Derive Hartree-Fock mean-field Hamiltonians and self-consistency equations from research-paper templates | Expert scores each response on Adherence, Rigor, Knowledge, Correctness using 0 / 50 / 100 | Measures execution of a specific analytic calculation workflow across papers |
| CURIE HFD-style tasks | Long-context paper-grounded scientific tasks, including Hartree-Fock derivation | Mixed metrics and expert/LLM similarity scoring depending on task type | Measures paper-grounded scientific understanding across heterogeneous domains |
| CMT-Benchmark | Expert-designed condensed-matter theory problems | Machine grading, including symbolic checks and non-commuting operator handling | Measures exact-answer CMT problem solving with objective grading |
| TPBench | Theoretical physics problem solving across difficulty levels | Auto-verifiable answer checks plus broader grading | Measures theoretical-physics reasoning and final-answer correctness |
| Our v0.1 toric-code task | Reconstruct a known topological-order derivation from prompt-level knowledge | Machine JSON verifier for `hard_score`; diagnostic rubric only for failure analysis | Measures agent capability profile for later Kimi-agent modification |

## Hard Score vs Rubric

For benchmark comparison, the primary score should be hard whenever possible.
In other benchmark papers, "rubric" can mean two different things:

1. A hard grading protocol: exact answer, unit test, symbolic equivalence,
   numerical tolerance, or machine-verifiable checkpoint.
2. A human/expert rubric: useful when derivation quality cannot be fully reduced
   to an exact answer, but weaker as a leaderboard score.

For our benchmark, use the same separation:

- `hard_score`: ability score for comparing agents;
- `diagnostic_profile`: secondary rubric for explaining failures and deciding
  what to change in the agent/harness.

The hard score wins if it disagrees with the diagnostic rubric.

## What Is Different About Our Rubric

Our rubric is more agent-engineering oriented than leaderboard oriented.

It separates:

- final result recovery;
- derivation core;
- assumptions and conventions;
- physics sanity checks;
- source grounding;
- uncertainty and claim control;
- failure tags that can map to harness changes.

This makes it useful for deciding what to modify in an agent, but weaker for
public model comparison unless task prompts, sources, and grading are frozen and
audited.

## Current Weaknesses

The current toric-code task is too easy to memorize and too under-specified as a
paper-grounded derivation benchmark.

Known gaps:

- no supplied paper/source packet;
- weak source-grounding signal;
- mechanized verifier exists for the current structured JSON fields, but no CAS
  or symbolic equivalence checker yet;
- one task cannot distinguish memorized theorem recall from robust derivation;
- manual expert judgment is now secondary, but still needed for richer failure
  diagnosis.

## Required Upgrade Before Serious Evaluation

Before using this as a real agent capability benchmark, add:

1. paper-grounded derivation tasks with provided excerpts/equations;
2. task-specific hidden-assumption traps;
3. a mechanized final-answer checker where possible;
4. two-rollout or three-rollout variance tracking;
5. explicit comparison against `kimi_project_default` and modified Kimi on the
   same frozen task revision.

## Source Pointers

- Quantum many-body Hartree-Fock benchmark:
  `https://www.nature.com/articles/s42005-025-01956-y`
- CURIE:
  `https://research.google/blog/evaluating-progress-of-llms-on-scientific-problem-solving/`
- CMT-Benchmark:
  `https://arxiv.org/abs/2510.05228`
- TPBench:
  `https://tpbench.org/`
