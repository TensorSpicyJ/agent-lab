# Agent And Benchmark Integration

Date: 2026-05-30

This note explains how the physics derivation framework is used both inside an
agent and inside a benchmark.

## Shared Contract

The archival contract is the `derivation_record`. The runtime benchmark
contract may be the smaller `answer_card`.

Agent side:

- keep a live `derivation_record` or equivalent internal state while solving
  the task;
- block unlicensed assumptions from entering the derivation trace;
- expose either a full record or a compact answer card at checkpoint or final
  answer time.

Benchmark side:

- require a final `derivation_record` or task-specific subset;
- run schema checks;
- run task-specific hard checks on selected fields;
- score failure modes using the same object.

The same framework should therefore answer two questions:

1. Can the agent reason safely?
2. Can the benchmark verify that reasoning without trusting the agent's prose?

For single-capability tests, prefer the answer-card protocol in
`ANSWER-CARD-PROTOCOL.md`. The harness can expand the card into a full
`derivation_record` using task-provided premises and source metadata.

## Runtime Loop

```text
input prompt/source
  -> premise_extractor
  -> translation_builder
  -> assumption_proposer
  -> approximation_gate
  -> deriver
  -> verifier
  -> derivation_record + final_answer
```

The gate is allowed to return three non-final outcomes:

- `reject`: the proposed assumption must not be used.
- `branch`: the answer must be conditional on the assumption.
- `request_info`: the derivation cannot proceed without additional regime or
  source information.

For benchmark tasks, `request_info` should usually be represented as a valid
answer only when the task is intentionally under-specified.

## Scoring Implications

The benchmark should separately score:

1. final result;
2. translation correctness;
3. assumption discipline;
4. derivation trace validity;
5. physics sanity checks.

This avoids a common false pass: correct final value reached through invalid or
unsupported physical assumptions.

## Attribution And Probe Tests

The benchmark should never force a psychological explanation when the structure
does not support one.

Use this rule:

```text
If the verifier can uniquely localize the first invalid node, record a strict
failure attribution.

If the verifier can only produce multiple candidate causes, record those
candidates and generate probe tests.

If the explanation depends on why the model behaved that way, mark it
diagnostic-only and keep it out of hard scoring.
```

Probe tests are small controlled variants. They should change one thing at a
time:

- convention;
- missing or added regime;
- boundary condition;
- topology;
- known limit;
- source excerpt wording;
- minimal counterexample.

The probe result can promote a candidate cause to strict localization only when
the new test gives a mechanically checkable distinction.

## Minimum Agent Implementation

For the first Kimi-based implementation, do not build a full theorem prover.
Start with a prompt/harness contract:

- require the agent to maintain an assumption ledger;
- require every derivation step to list dependencies;
- forbid derivation steps from depending on rejected or unresolved assumptions;
- require explicit branches when a regime is missing;
- run a deterministic verifier on the final record.

## Future Strengthening

The framework can be strengthened incrementally:

1. JSON schema validation only.
2. Task-specific Python verifier.
3. SymPy or CAS equivalence checks.
4. Random hidden generated instances.
5. Lean or another proof assistant for narrow exact cores.

The agent protocol should stay stable across these levels.
