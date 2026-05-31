# Run Notes

This run uses the compact answer-card protocol.

Result:

```text
hard_score = 15 / 15 = 1.0
```

Why compact mode:

- The full `derivation_record` prompt caused Kimi CLI runs to exceed the local
  timeout and leave truncated JSON.
- The truncated full-record attempts showed the model understood the core
  assumption-gate physics, but output length and enum/schema verbosity made the
  run invalid for hard scoring.
- The answer-card protocol keeps the agent output short while preserving the
  hard-scored fields.

Artifacts:

- `outputs/band-effective-mass-assumption-gate.md`: raw Kimi answer card.
- `scores/band-effective-mass-assumption-gate.answer-card-score.json`: hard
  score from `verify_short.py`.
- `outputs/band-effective-mass-assumption-gate.derivation-record.json`: harness
  expansion into the full framework object.

