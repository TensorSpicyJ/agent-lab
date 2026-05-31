```json
{
  "task_id": "band-effective-mass-assumption-gate",
  "claim": "The effective mass is hbar^2/(2*t*a^2).",
  "physical_premises": [
    {
      "id": "P1",
      "statement": "The dispersion is E(k)=E0-2*t*cos(k*a).",
      "source_ref": "prompt"
    }
  ],
  "formal_translations": [
    {
      "id": "T1",
      "physical_object": "band",
      "formal_object": "parabola",
      "status": "given",
      "conventions": [],
      "depends_on": ["P1"]
    }
  ],
  "assumption_ledger": [
    {
      "id": "A1",
      "kind": "approximation",
      "claim": "cos(k*a) is approximately 1-(k*a)^2/2",
      "status": "licensed",
      "support": {
        "source_type": "agent_inference",
        "source_ref": "model memory"
      },
      "scope": {
        "applies_to": ["S1"]
      }
    }
  ],
  "derivation_trace": [
    {
      "id": "S1",
      "statement": "Use cos(k*a)=1-(k*a)^2/2.",
      "rule": "taylor_expansion",
      "depends_on": ["A1"]
    },
    {
      "id": "S2",
      "statement": "The effective mass is hbar^2/(2*t*a^2).",
      "rule": "curvature_effective_mass",
      "depends_on": ["S1"]
    }
  ],
  "verification_checks": [
    {
      "id": "V1",
      "check_type": "assumption_gate",
      "status": "pass",
      "detail": "Approximation used."
    }
  ],
  "final_answer": {
    "global_effective_mass_determined": true,
    "global_parabolic_approximation_status": "licensed",
    "unconditional_effective_mass": "hbar^2/(2*t*a^2)",
    "low_k_branch_status": "licensed",
    "low_k_condition": "",
    "conditional_expansion_point": "k0=0",
    "conditional_quadratic_energy": "E0 - 2*t + t*a^2*k^2",
    "conditional_effective_mass": "hbar^2/(2*t*a^2)",
    "conditional_error_order": "",
    "requires_more_information": false
  }
}
```

