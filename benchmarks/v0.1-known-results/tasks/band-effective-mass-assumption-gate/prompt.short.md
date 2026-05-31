# Benchmark Task: Effective-Mass Assumption Gate

Do not search. Use only this prompt.

Source facts:

- `E(k) = E0 - 2 t cos(k a)`, with `t > 0`.
- Effective mass is local near a specified extremum `k0`.
- `E(k0+q) = E(k0) + (1/2)E''(k0)q^2 + ...`.
- Matching to `E(k0+q)=E(k0)+hbar^2 q^2/(2m*)` gives
  `m* = hbar^2/E''(k0)`.
- The approximation is valid only for small `|q a|` around the chosen `k0`.
- `cos(k a) ~= 1 - (k a)^2/2` is local around `k0=0`, not global.

Task: Given only `E(k)=E0-2t cos(k a)`, decide what can and cannot be concluded
about effective mass. The prompt does not give a low-energy regime, expansion
point, or global `|k a| << 1`.

Return only this JSON shape:

```json
{
  "task_id": "band-effective-mass-assumption-gate",
  "claim": "short conclusion",
  "assumption_ledger": [
    {
      "id": "A1",
      "kind": "approximation",
      "claim": "global parabolic approximation",
      "status": "rejected",
      "valid_when": "never globally",
      "invalid_when": "prompt gives no global |ka| << 1"
    },
    {
      "id": "A2",
      "kind": "regime",
      "claim": "low-k branch around k0=0",
      "status": "conditional",
      "valid_when": "|ka| << 1 near k0=0",
      "invalid_when": "away from k0=0"
    }
  ],
  "steps": [
    {"id": "S1", "rule": "refusal_without_regime", "depends_on": ["A1"], "statement": "no global effective mass is determined"},
    {"id": "S2", "rule": "conditional_branch", "depends_on": ["A2"], "statement": "if |ka| << 1 near k0=0, expand locally"},
    {"id": "S3", "rule": "curvature_effective_mass", "depends_on": ["S2"], "statement": "m* = hbar^2/(2*t*a^2)"}
  ],
  "final_answer": {
    "global_effective_mass_determined": false,
    "global_parabolic_approximation_status": "rejected",
    "unconditional_effective_mass": null,
    "low_k_branch_status": "conditional",
    "low_k_condition": "|ka| << 1 near k0=0",
    "conditional_expansion_point": "k0=0",
    "conditional_quadratic_energy": "E0 - 2*t + t*a^2*k^2",
    "conditional_effective_mass": "hbar^2/(2*t*a^2)",
    "conditional_error_order": "O((k*a)^4)",
    "requires_more_information": true
  }
}
```

