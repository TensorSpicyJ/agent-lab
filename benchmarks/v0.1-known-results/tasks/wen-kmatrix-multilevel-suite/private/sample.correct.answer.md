```json
{
  "task_id": "wen-kmatrix-multilevel-suite",
  "source_excerpt_used": "wen-kmatrix-multilevel-minimal",
  "level_1": {
    "det_K": 3,
    "filling_fraction": "2/3",
    "torus_gsd": 3,
    "genus_gsd": 9,
    "charges": {"l1": "1/3", "l2": "0"},
    "statistics_theta_over_pi": {"l1": "2/3", "l2": "2"}
  },
  "level_2": {
    "anyon_lattice": "Z^2 / K Z^2",
    "snf_invariant_factors": [1, 3],
    "quotient_group": "Z_3",
    "representatives": [[0, 0], [1, 0], [2, 0]],
    "derivation_steps": [
      {"id": "L2S1", "rule": "local_particle_quotient", "statement": "Local particles identify l ~ l + K n, so sectors are Z^2/KZ^2.", "depends_on": []},
      {"id": "L2S2", "rule": "smith_normal_form_or_index", "statement": "SNF gives invariant factors [1,3], hence quotient Z_3 with order 3.", "depends_on": ["L2S1"]},
      {"id": "L2S3", "rule": "torus_sector_count", "statement": "Torus GSD counts sectors, so GSD=3.", "depends_on": ["L2S2"]}
    ]
  },
  "level_3": {
    "nodes": [
      {"id": "source_anyon_vectors", "type": "source", "claim": "quasiparticles are integer vectors l"},
      {"id": "source_local_particle_equivalence", "type": "source", "claim": "l ~ l + K n"},
      {"id": "translation_quotient_lattice", "type": "translation", "claim": "sectors are Z^2/KZ^2"},
      {"id": "math_finite_index_or_snf", "type": "math_lemma", "claim": "|Z^2/KZ^2|=|det K|"},
      {"id": "physical_bridge_torus_gsd_counts_sectors", "type": "physical_bridge", "claim": "torus GSD counts topological sectors"}
    ],
    "edges": [
      ["source_anyon_vectors", "translation_quotient_lattice"],
      ["source_local_particle_equivalence", "translation_quotient_lattice"],
      ["translation_quotient_lattice", "math_finite_index_or_snf"],
      ["math_finite_index_or_snf", "physical_bridge_torus_gsd_counts_sectors"]
    ],
    "final_claim": "GSD_torus = |det K|"
  },
  "level_4": {
    "section_links": [
      {"from": "bulk_K_data", "to": "anyon_quotient", "relation": "K defines local particle quotient"},
      {"from": "anyon_quotient", "to": "torus_gsd", "relation": "torus GSD counts sectors"},
      {"from": "bulk_K_data", "to": "edge_signature", "relation": "signature(K) controls chirality"},
      {"from": "edge_signature", "to": "edge_mode_count", "relation": "positive eigenvalues give right movers"}
    ],
    "edge": {
      "num_edge_fields": 2,
      "num_right_movers": 2,
      "num_left_movers": 0,
      "net_chirality": 2,
      "bulk_edge_connection_is_physical_bridge": true
    }
  },
  "claim_control": {
    "no_novelty_claim": true,
    "does_not_claim_real_material_identification": true
  }
}
```

