# Task: Derive Filling-Fraction Invariance Under K-Matrix Basis Change

Read:

```text
source_packet/basis_transform_excerpt.md
```

You are given a visible K-matrix instance:

```json
{
  "K": [[3, 1], [1, 3]],
  "t": [1, 1],
  "W": [[1, 1], [0, 1]]
}
```

## Goal

Show that the filling fraction is invariant under the basis transform:

```text
K_prime = W^T K W
t_prime = W^T t
nu = t^T K^{-1} t
nu_prime = t_prime^T K_prime^{-1} t_prime
```

## Requirements

1. Give a short prose derivation.
2. Do not use web search.
3. Do not claim novelty.
4. End with a machine-gradable JSON block.

## Machine-Graded JSON Fields

```text
task_id: "wen-kmatrix-basis-invariance"
derivation_claim: "nu_prime = nu"
steps: array of derivation steps
K_prime: transformed matrix
t_prime: transformed charge vector
nu: exact rational string
nu_prime: exact rational string
invariant: boolean
no_novelty_claim: boolean
source_excerpt_used: "wen-kmatrix-basis-transform-minimal"
```

Each derivation step must have:

```json
{
  "id": "S1",
  "statement": "...",
  "rule": "...",
  "depends_on": []
}
```

Allowed rules:

```text
matrix_basis_transform
inverse_of_transformed_K
substitution
matrix_associativity
unimodular_invertibility
scalar_equality
numeric_instance_check
```
