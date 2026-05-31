# Task: Wen K-Matrix Laughlin Hidden-Parameter Check

You are given a source packet that summarizes the K-matrix formalism used in
Wen's discussion of Abelian FQH topological orders.

Read:

```text
source_packet/wen_kmatrix_excerpt.md
```

Then solve the generated Laughlin-state instance below.

## Visible Instance

```json
{
  "K": [[7]],
  "t": [1],
  "genus": 2,
  "l_vectors": [[1], [2]]
}
```

## Requirements

1. Use only the source packet and the visible instance.
2. Do not use web search.
3. Do not claim this result is novel.
4. Show a short derivation in prose.
5. End with a machine-gradable JSON block with the fields below.

## Output Fields

| Field | Type | Description |
| --- | --- | --- |
| `task_id` | string | Must be `"wen-kmatrix-laughlin-hidden-m"` |
| `det_K` | integer | Determinant of the visible `K` matrix |
| `filling_fraction` | string | Exact rational value of `t^T K^{-1} t` |
| `torus_gsd` | integer | Ground-state degeneracy on a torus |
| `genus_gsd` | integer | Ground-state degeneracy on the visible genus surface |
| `quasiparticles` | array | One entry per visible `l` vector, in the same order |
| `quasiparticles[].l` | integer array | The visible quasiparticle vector |
| `quasiparticles[].charge` | string | Exact rational value of `t^T K^{-1} l` |
| `quasiparticles[].exchange_statistics_theta_over_pi` | string | Exact rational value of `l^T K^{-1} l` |
| `no_novelty_claim` | boolean | Must be `true` |
| `source_excerpt_used` | string | Must be `"wen-kmatrix-formulas-minimal"` |

Use exact rational strings such as `"1/7"`, not decimals.
