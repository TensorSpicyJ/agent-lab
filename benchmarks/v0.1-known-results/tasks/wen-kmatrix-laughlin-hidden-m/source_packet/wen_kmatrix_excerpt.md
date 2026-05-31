# Source Packet: Wen K-Matrix Formalism Excerpt

Source basis:

- Xiao-Gang Wen, "Topological orders and Edge excitations in FQH states",
  arXiv:cond-mat/9506066.

This packet is a benchmark excerpt, not a complete paper copy. It contains only
the method formulas needed for the task.

## Excerpt

In the Abelian fractional quantum Hall K-matrix description, an Abelian
topological order is described by an integer, symmetric, non-singular matrix
`K` and an integer charge vector `t`.

For a quasiparticle labeled by an integer vector `l`, the standard response and
statistics quantities are computed from `K^{-1}`:

```text
filling fraction:           nu = t^T K^{-1} t
quasiparticle charge:       q_l = t^T K^{-1} l
exchange statistics:        theta_l / pi = l^T K^{-1} l
mutual statistics / 2pi:    M(l1,l2) = l1^T K^{-1} l2
```

For an Abelian topological order described by `K`, the ground-state degeneracy
on a torus is:

```text
GSD_torus = |det K|
```

On a closed orientable genus-`g` surface, the corresponding degeneracy is:

```text
GSD_genus_g = |det K|^g
```

For a one-component Laughlin state, the K matrix is `K = [m]` and the charge
vector is `t = [1]`, where `m` is an odd positive integer.

## Excerpt Manifest

```yaml
excerpt_id: wen-kmatrix-formulas-minimal
source: "Wen 1995, arXiv:cond-mat/9506066"
role: method_formula
contains_gold_answer: false
leakage_risk: low
notes: "Contains general formulas; task parameters are generated separately."
```
