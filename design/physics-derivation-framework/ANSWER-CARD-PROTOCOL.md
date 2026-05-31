# Answer Card Protocol

Date: 2026-05-30

The full `derivation_record` is the archival and attribution object. It is not
always the right object for an LLM to emit directly.

For benchmark runs, prefer a two-layer protocol:

1. Agent emits a compact `answer_card`.
2. Harness verifies the card and expands it into a full `derivation_record` when
   archival detail is needed.

## Why

Long JSON records create avoidable failures:

- model spends tokens restating source facts;
- CLI wrappers may timeout or truncate output;
- schema pressure encourages invalid enum values;
- formatting failures can hide whether the physics decision was correct.

The answer card keeps the hard-scored fields small while preserving the same
framework semantics.

## Agent Output

The agent should emit only:

- `task_id`;
- one-sentence `claim`;
- compact `assumption_ledger`;
- compact `steps`;
- `final_answer`.

Use `schemas/answer-card.schema.json`.

## Harness Expansion

The harness may expand the answer card into a full `derivation_record` by adding:

- task-provided physical premises;
- task-provided formal translations;
- source excerpt references;
- normalized verification checks;
- answer-card steps as `derivation_trace`.

This keeps benchmark scoring strict without requiring the agent to reproduce
boilerplate.

## Rule

Use full `derivation_record` when testing long-form research reporting.
Use `answer_card` when testing a single capability such as assumption gating,
source grounding, convention handling, or one derivation step.

