# Source Packet: Tight-Binding Effective Mass

Excerpt id: `tight-binding-effective-mass-minimal`

This packet gives the method but not the benchmark answer.

For a one-dimensional nearest-neighbor tight-binding band,

```text
E(k) = E0 - 2 t cos(k a)
```

where `t > 0` is the hopping amplitude and `a` is the lattice spacing.

An effective mass approximation is local in momentum space. It is defined by
expanding the band near a specified extremum `k0`:

```text
E(k0 + q) = E(k0) + (1/2) E''(k0) q^2 + higher-order terms
```

and matching the quadratic term to

```text
E(k0 + q) = E(k0) + hbar^2 q^2 / (2 m*)
```

so that

```text
m* = hbar^2 / E''(k0)
```

This approximation is valid only for sufficiently small `|q a|` around the
chosen extremum. The expression `cos(k a) ≈ 1 - (k a)^2 / 2` is a small-`ka`
expansion around `k0 = 0`, not a global approximation over the Brillouin zone.

