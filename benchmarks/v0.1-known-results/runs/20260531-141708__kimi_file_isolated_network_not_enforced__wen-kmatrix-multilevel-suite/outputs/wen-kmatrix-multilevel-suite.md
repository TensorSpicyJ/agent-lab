• ```json
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
        {"id": "L2S1", "rule": "local_particle_quotient", "statement": "Distinct anyon sectors are equivalence classes in Z^2 / K Z^2, identifying l ~ l + K n for n in Z^2.", "depends_on": []},
        {"id": "L2S2", "rule": "smith_normal_form_or_index", "statement": "The finite index of the quotient lattice equals |det K| = 3. Smith normal form of K yields invariant factors [1, 3] with product 3 = |det K|.", "depends_on": ["L2S1"]},
        {"id": "L2S3", "rule": "torus_sector_count", "statement": "GSD_torus = |Z^2 / K Z^2| = |det K| = 3.", "depends_on": ["L2S2"]}
      ]
    },
    "level_3": {
      "nodes": [
        {"id": "source_anyon_vectors", "type": "source", "claim": "Quasiparticle types are labeled by integer vectors l."},
        {"id": "source_local_particle_equivalence", "type": "source", "claim": "Vectors that differ by a local particle are identified: l ~ l + K n for n in Z^N."},
        {"id": "translation_quotient_lattice", "type": "math", "claim": "Distinct Abelian anyon sectors are equivalence classes in the quotient lattice Z^N / K Z^N."},
        {"id": "math_finite_index_or_snf", "type": "math", "claim": "For full-rank integer K, the number of equivalence classes is the finite index |Z^N / K Z^N| = |det K|."},
        {"id": "physical_bridge_torus_gsd_counts_sectors", "type": "physical", "claim": "On a torus, the topological ground-state degeneracy counts the distinct topological sectors: GSD_torus = |Z^N / K Z^N| = |det K|."}
      ],
      "edges": [
        ["source_anyon_vectors", "source_local_particle_equivalence"],
        ["source_local_particle_equivalence", "translation_quotient_lattice"],
        ["translation_quotient_lattice", "math_finite_index_or_snf"],
        ["math_finite_index_or_snf", "physical_bridge_torus_gsd_counts_sectors"]
      ],
      "final_claim": "GSD_torus = |det K|"
    },
    "level_4": {
      "section_links": [
        {"from": "bulk_K_data", "to": "anyon_quotient", "relation": "The integer K matrix defines local-particle equivalence l ~ l + K n, whose equivalence classes form the anyon quotient Z^N / K Z^N."},
        {"from": "anyon_quotient", "to": "torus_gsd", "relation": "The number of distinct anyon sectors (the finite index of the quotient lattice) equals the torus ground-state degeneracy GSD_torus = |det K|."},
        {"from": "bulk_K_data", "to": "edge_signature", "relation": "The signature of K (number of positive vs negative eigenvalues) determines the edge-mode chirality."},
        {"from": "edge_signature", "to": "edge_mode_count", "relation": "Positive eigenvalues count right-moving edge modes and negative eigenvalues count left-moving edge modes."}
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

