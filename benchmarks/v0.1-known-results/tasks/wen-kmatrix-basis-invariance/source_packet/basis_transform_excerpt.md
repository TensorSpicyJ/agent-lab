# Source Packet: K-Matrix Basis Transform

Source basis:

- Xiao-Gang Wen, "Topological orders and Edge excitations in FQH states",
  arXiv:cond-mat/9506066.

This packet contains a minimal method excerpt for basis changes in the Abelian
K-matrix formalism.

## Excerpt

An Abelian FQH topological order can be represented by an integer symmetric
non-singular matrix `K` and an integer charge vector `t`. The filling fraction
is:

```text
nu = t^T K^{-1} t
```

A change of integer quasiparticle basis by a unimodular integer matrix `W`
preserves the underlying topological order. In this convention:

```text
K_prime = W^T K W
t_prime = W^T t
```

Physical scalar quantities such as the filling fraction should be invariant
under this change of basis.

## Excerpt Manifest

```yaml
excerpt_id: wen-kmatrix-basis-transform-minimal
source: "Wen 1995, arXiv:cond-mat/9506066"
role: method_derivation_prompt
contains_gold_answer: false
leakage_risk: low
notes: "Gives transformation rules but not the hidden instance result."
```
