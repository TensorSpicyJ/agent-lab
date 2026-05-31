# Hard Scoring Policy

Date: 2026-05-30

## Rule

The benchmark score must be hard to argue with.

Primary scores must come from deterministic verifiers:

- exact symbolic or numeric answers;
- JSON schema checks;
- formula equivalence checks;
- unit or dimension checks;
- tolerance-based numerical comparisons;
- proof-assistant or CAS checks when available;
- source-span retrieval checks when the task is source-grounded.

Human or LLM rubrics are allowed only for secondary failure analysis.

Hard scoring is not enough by itself. Runs must also satisfy the anti-leakage
policy in `ANTI-LEAKAGE-POLICY.md`; otherwise a correct hard score may only
show that the agent found or memorized the answer.

## Why

Manual diagnostic rubrics can be useful, but they are not stable enough to be
the capability criterion. If the scorer can explain away a result, the benchmark
is not serving as a benchmark.

## Score Layers

1. `hard_score`: ability score, used for agent comparison.
2. `diagnostic_profile`: explanation layer, used to decide what to improve.

If the two disagree, `hard_score` wins.

## Derivation Task Design

A derivation task should expose hard checkable targets:

- final value or formula;
- required intermediate equations;
- required assumptions as structured booleans or enums;
- known-limit or special-case outputs;
- prohibited claims such as novelty or unsupported caveats.

The prose derivation can still be reviewed, but it must not be the only grade.

## Current Example

`toric-code-gsd-basic` now requires a machine-gradable JSON block and is checked
by `tasks/toric-code-gsd-basic/verify.py`.

Kimi Code project-default run
`20260530-145803__kimi_project_default__toric-code-gsd-basic` scored:

```text
hard_score = 17 / 17 = 1.0
```

This is the valid baseline for this task revision.
