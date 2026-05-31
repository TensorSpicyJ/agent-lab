# Source Packet: Wen K-Matrix Multilevel Suite

Excerpt id: `wen-kmatrix-multilevel-minimal`

Source basis: Xiao-Gang Wen, "Topological orders and Edge excitations in FQH
states", arXiv:cond-mat/9506066 / Advances in Physics 44, 405 (1995).

This packet is a controlled benchmark excerpt. It gives the method and local
formalism, but not the generated instance answers.

## Abelian K-Matrix Data

An Abelian FQH topological order can be described by an integer symmetric
non-singular K matrix and an integer charge vector t.

The filling fraction is

```text
nu = t^T K^{-1} t .
```

Quasiparticle types are labeled by integer vectors l. Their electric charge and
exchange statistics are computed as

```text
q_l = t^T K^{-1} l
theta_l / pi = l^T K^{-1} l .
```

## Local Particles And Anyon Sectors

Vectors that differ by a local particle are identified:

```text
l ~ l + K n,  n in Z^N .
```

Thus distinct Abelian anyon sectors are equivalence classes in the quotient
lattice

```text
Z^N / K Z^N .
```

For a full-rank integer K, the number of such equivalence classes is the finite
index

```text
|Z^N / K Z^N| = |det K| .
```

Equivalently, the Smith normal form of K gives invariant factors d_i, and the
quotient group is

```text
Z_{d1} x Z_{d2} x ... ,
```

with product `d1 d2 ... = |det K|`.

## Torus Ground-State Degeneracy

On a torus, the topological ground-state degeneracy counts the distinct
topological sectors. In this Abelian K-matrix setting,

```text
GSD_torus = |Z^N / K Z^N| = |det K| .
```

For genus g, the corresponding formula is

```text
GSD_genus_g = |det K|^g .
```

## Edge Chirality

The edge theory contains one chiral boson for each K-matrix component. The
numbers of right- and left-moving edge modes are determined by the signature of
K: positive eigenvalues give right-moving modes, negative eigenvalues give
left-moving modes. The net chirality is

```text
c_- = signature(K) = n_+ - n_- .
```

This edge statement is a physical bridge from the bulk K data to edge-mode
content; it is not the same kind of statement as a pure determinant calculation.

