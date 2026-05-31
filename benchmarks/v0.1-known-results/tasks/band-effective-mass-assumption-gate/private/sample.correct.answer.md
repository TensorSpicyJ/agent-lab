```json
{
  "task_id": "band-effective-mass-assumption-gate",
  "claim": "The prompt does not determine an unconditional global effective mass; a low-k effective mass follows only conditionally near k0=0 with |k*a| << 1.",
  "physical_premises": [
    {
      "id": "P1",
      "statement": "The dispersion is E(k)=E0-2*t*cos(k*a) with t>0.",
      "source_ref": "prompt"
    },
    {
      "id": "P2",
      "statement": "The source packet states that effective mass is a local approximation near a specified extremum.",
      "source_ref": "tight-binding-effective-mass-minimal"
    }
  ],
  "formal_translations": [
    {
      "id": "T1",
      "physical_object": "one-dimensional tight-binding band",
      "formal_object": "function E(k)=E0-2*t*cos(k*a)",
      "status": "given",
      "conventions": ["t > 0", "a is lattice spacing"],
      "depends_on": ["P1"]
    },
    {
      "id": "T2",
      "physical_object": "effective mass near an extremum",
      "formal_object": "m* = hbar^2 / E''(k0)",
      "status": "given",
      "conventions": ["local expansion in q around k0"],
      "depends_on": ["P2"]
    }
  ],
  "assumption_ledger": [
    {
      "id": "A1",
      "kind": "approximation",
      "claim": "Treating cos(k*a) as 1-(k*a)^2/2 over the whole Brillouin zone is a global parabolic approximation.",
      "status": "rejected",
      "support": {
        "source_type": "source_excerpt",
        "source_ref": "tight-binding-effective-mass-minimal",
        "quote_or_summary": "The source says the small-ka expansion is local around k0=0, not global."
      },
      "scope": {
        "applies_to": ["S1"],
        "valid_when": "not valid globally",
        "invalid_when": "the prompt gives no low-energy regime or specified expansion point"
      },
      "small_or_large_parameter": "k*a",
      "error_order": "not licensed globally",
      "checks": [
        {
          "check_type": "source_consistency",
          "status": "pass",
          "detail": "The source explicitly warns that the small-ka expansion is not global."
        }
      ]
    },
    {
      "id": "A2",
      "kind": "regime",
      "claim": "A low-k branch around k0=0 may be derived if |k*a| << 1 is added.",
      "status": "conditional",
      "support": {
        "source_type": "source_excerpt",
        "source_ref": "tight-binding-effective-mass-minimal",
        "quote_or_summary": "Effective mass is defined by local expansion near a specified extremum."
      },
      "scope": {
        "applies_to": ["S2", "S3"],
        "valid_when": "|k*a| << 1 near k0=0",
        "invalid_when": "away from the local neighborhood of k0=0"
      },
      "small_or_large_parameter": "k*a",
      "error_order": "O((k*a)^4)",
      "checks": [
        {
          "check_type": "known_limit",
          "status": "pass",
          "detail": "At k=0 the band minimum has positive curvature for t>0."
        }
      ]
    }
  ],
  "derivation_trace": [
    {
      "id": "S1",
      "statement": "Because no expansion point or low-energy regime is specified, the global parabolic approximation is not licensed.",
      "rule": "refusal_without_regime",
      "depends_on": ["P1", "P2", "A1"]
    },
    {
      "id": "S2",
      "statement": "Conditional on |k*a| << 1 near k0=0, cos(k*a)=1-(k*a)^2/2+O((k*a)^4).",
      "rule": "conditional_branch",
      "depends_on": ["A2"]
    },
    {
      "id": "S3",
      "statement": "Then E(k)=E0-2*t+t*a^2*k^2+O((k*a)^4), so m*=hbar^2/(2*t*a^2).",
      "rule": "curvature_effective_mass",
      "depends_on": ["S2", "T2"]
    },
    {
      "id": "S4",
      "statement": "The conditional result does not determine a global effective mass.",
      "rule": "assumption_gate",
      "depends_on": ["S1", "S3"]
    }
  ],
  "verification_checks": [
    {
      "id": "V1",
      "check_type": "assumption_gate",
      "status": "pass",
      "detail": "The unsupported global approximation is rejected and the low-k result is conditional."
    },
    {
      "id": "V2",
      "check_type": "known_limit",
      "status": "pass",
      "detail": "The k0=0 branch has E''(0)=2*t*a^2 and positive effective mass."
    }
  ],
  "final_answer": {
    "global_effective_mass_determined": false,
    "global_parabolic_approximation_status": "rejected",
    "unconditional_effective_mass": null,
    "low_k_branch_status": "conditional",
    "low_k_condition": "|k*a| << 1 near k0=0",
    "conditional_expansion_point": "k0=0",
    "conditional_quadratic_energy": "E0 - 2*t + t*a^2*k^2",
    "conditional_effective_mass": "hbar^2/(2*t*a^2)",
    "conditional_error_order": "O((k*a)^4)",
    "requires_more_information": true
  }
}
```

