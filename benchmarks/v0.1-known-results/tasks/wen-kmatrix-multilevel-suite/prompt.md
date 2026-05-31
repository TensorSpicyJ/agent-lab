# Benchmark Task: Wen K-Matrix Multilevel Suite

Do not search the web. Use only this prompt and the source packet:

```text
source_packet/wen_kmatrix_multilevel_excerpt.md
```

You are given this generated instance:

```json
{
  "K": [[2, 1], [1, 2]],
  "t": [1, 1],
  "genus": 2,
  "l_vectors": {
    "l1": [1, 0],
    "l2": [1, -1]
  }
}
```

Return exactly one fenced JSON object. No prose outside the JSON block.

## Levels

### Level 1: Formula Application

Compute:

- `det_K`
- `filling_fraction = t^T K^{-1} t`
- `torus_gsd = |det K|`
- `genus_gsd = |det K|^genus`
- charge and exchange statistics for `l1` and `l2`

### Level 2: Local Derivation

Derive the torus GSD from the quotient lattice:

```text
distinct anyons = Z^2 / K Z^2
|Z^2 / K Z^2| = |det K|
GSD_torus = |det K|
```

Also provide the Smith normal form invariant factors and one valid set of three
representatives for the quotient classes.

### Level 3: Bridge Derivation

Build a dependency graph connecting source fragments to the final GSD claim.
The graph must include nodes with these exact ids:

```text
source_anyon_vectors
source_local_particle_equivalence
translation_quotient_lattice
math_finite_index_or_snf
physical_bridge_torus_gsd_counts_sectors
```

It must include edges showing how the physical source claims become the
mathematical quotient and then become the torus GSD.

### Level 4: Section-Level Connection

Connect bulk K data to both:

- bulk topological sectors / torus GSD;
- edge mode chirality.

This level tests whether you can connect different parts of the source packet,
not only compute formulas.

## Required JSON Shape

```json
{
  "task_id": "wen-kmatrix-multilevel-suite",
  "source_excerpt_used": "wen-kmatrix-multilevel-minimal",
  "level_1": {
    "det_K": 0,
    "filling_fraction": "...",
    "torus_gsd": 0,
    "genus_gsd": 0,
    "charges": {"l1": "...", "l2": "..."},
    "statistics_theta_over_pi": {"l1": "...", "l2": "..."}
  },
  "level_2": {
    "anyon_lattice": "Z^2 / K Z^2",
    "snf_invariant_factors": [0, 0],
    "quotient_group": "...",
    "representatives": [[0, 0]],
    "derivation_steps": [
      {"id": "L2S1", "rule": "local_particle_quotient", "statement": "...", "depends_on": []},
      {"id": "L2S2", "rule": "smith_normal_form_or_index", "statement": "...", "depends_on": ["L2S1"]},
      {"id": "L2S3", "rule": "torus_sector_count", "statement": "...", "depends_on": ["L2S2"]}
    ]
  },
  "level_3": {
    "nodes": [
      {"id": "source_anyon_vectors", "type": "source", "claim": "..."}
    ],
    "edges": [
      ["source_anyon_vectors", "translation_quotient_lattice"]
    ],
    "final_claim": "GSD_torus = |det K|"
  },
  "level_4": {
    "section_links": [
      {"from": "bulk_K_data", "to": "anyon_quotient", "relation": "..."},
      {"from": "anyon_quotient", "to": "torus_gsd", "relation": "..."},
      {"from": "bulk_K_data", "to": "edge_signature", "relation": "..."},
      {"from": "edge_signature", "to": "edge_mode_count", "relation": "..."}
    ],
    "edge": {
      "num_edge_fields": 0,
      "num_right_movers": 0,
      "num_left_movers": 0,
      "net_chirality": 0,
      "bulk_edge_connection_is_physical_bridge": true
    }
  },
  "claim_control": {
    "no_novelty_claim": true,
    "does_not_claim_real_material_identification": true
  }
}
```

Use exact rational strings such as `"2/3"` when needed.

