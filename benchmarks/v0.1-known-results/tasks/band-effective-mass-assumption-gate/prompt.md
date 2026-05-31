# Benchmark Task: Assumption Gate For Effective Mass

You are solving a physics derivation benchmark. Do not search the web. Use only
the source packet and the task statement below.

## Source Packet

Excerpt id: `tight-binding-effective-mass-minimal`

For a one-dimensional nearest-neighbor tight-binding band,

```text
E(k) = E0 - 2 t cos(k a)
```

where `t > 0` is the hopping amplitude and `a` is the lattice spacing.

An effective mass approximation is local in momentum space. It is defined by
expanding the band near a specified extremum `k0`:

```text
E(k0 + q) = E(k0) + (1/2) E''(k0) q^2 + higher-order terms
```

and matching the quadratic term to

```text
E(k0 + q) = E(k0) + hbar^2 q^2 / (2 m*)
```

so that

```text
m* = hbar^2 / E''(k0)
```

This approximation is valid only for sufficiently small `|q a|` around the
chosen extremum. The expression `cos(k a) ≈ 1 - (k a)^2 / 2` is a small-`ka`
expansion around `k0 = 0`, not a global approximation over the Brillouin zone.

## Task

Given only

```text
E(k) = E0 - 2 t cos(k a),  t > 0
```

derive what can and cannot be concluded about an effective mass.

Important: the prompt does **not** specify a low-energy regime, an expansion
point, or that `|k a| << 1` globally.

Your answer must follow the physics derivation framework:

- separate physical premises from formal translations;
- keep an assumption ledger;
- reject or branch unsupported approximations;
- include a derivation trace;
- include verification checks;
- provide the final answer as a JSON object.

Return exactly one fenced JSON object. No prose outside the JSON block.

## Required JSON Shape

Use this shape. You may add concise text inside string fields, but do not add
extra top-level fields.

```json
{
  "task_id": "band-effective-mass-assumption-gate",
  "claim": "...",
  "physical_premises": [
    {
      "id": "P1",
      "statement": "...",
      "source_ref": "prompt"
    }
  ],
  "formal_translations": [
    {
      "id": "T1",
      "physical_object": "...",
      "formal_object": "...",
      "status": "given",
      "conventions": ["..."],
      "depends_on": ["P1"]
    }
  ],
  "assumption_ledger": [
    {
      "id": "A1",
      "kind": "approximation",
      "claim": "...",
      "status": "rejected",
      "support": {
        "source_type": "source_excerpt",
        "source_ref": "tight-binding-effective-mass-minimal",
        "quote_or_summary": "..."
      },
      "scope": {
        "applies_to": ["S1"],
        "valid_when": "...",
        "invalid_when": "..."
      },
      "small_or_large_parameter": "...",
      "error_order": "...",
      "checks": [
        {
          "check_type": "source_consistency",
          "status": "pass",
          "detail": "..."
        }
      ]
    }
  ],
  "derivation_trace": [
    {
      "id": "S1",
      "statement": "...",
      "rule": "assumption_gate",
      "depends_on": ["P1", "A1"]
    }
  ],
  "verification_checks": [
    {
      "id": "V1",
      "check_type": "assumption_gate",
      "status": "pass",
      "detail": "..."
    }
  ],
  "final_answer": {
    "global_effective_mass_determined": false,
    "global_parabolic_approximation_status": "rejected",
    "unconditional_effective_mass": null,
    "low_k_branch_status": "conditional",
    "low_k_condition": "...",
    "conditional_expansion_point": "k0=0",
    "conditional_quadratic_energy": "...",
    "conditional_effective_mass": "...",
    "conditional_error_order": "...",
    "requires_more_information": true
  }
}
```

