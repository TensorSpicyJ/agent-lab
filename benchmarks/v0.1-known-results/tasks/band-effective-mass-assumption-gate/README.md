# band-effective-mass-assumption-gate

Purpose: test whether an agent can prevent an unsupported approximation from
entering a physics derivation.

The task gives a nearest-neighbor tight-binding dispersion but deliberately
does not specify a low-energy regime or expansion point. The correct behavior
is:

- reject a global parabolic approximation;
- state that an unconditional effective mass is not determined from the prompt;
- optionally provide a conditional low-`k` branch around `k0=0`;
- record the approximation status in the assumption ledger;
- keep derivation steps dependent only on source facts, translations, and
  licensed or conditional assumptions.

This task uses the compact answer-card protocol as the primary runtime format:
`../../../../design/physics-derivation-framework/ANSWER-CARD-PROTOCOL.md`.

The longer `prompt.md` is kept as a full-record stress test. The primary Kimi
baseline should use `prompt.short.md` because it tests the assumption gate
without making output length the bottleneck.

Verifier:

```powershell
python benchmarks/v0.1-known-results/tasks/band-effective-mass-assumption-gate/verify_short.py <answer.md>
```
