# Web Physics Adversarial Result-Only Benchmark v0.1

Date: 2026-06-02

Purpose: push beyond textbook numerical substitution and the first hard quantum suite by testing physics translation choices that are easy to get subtly wrong.

## Scope

This benchmark remains result-only, but its fields target higher-level physics structure:

- degenerate perturbation theory with second-order coupling to an external state;
- Berry phase sign for a spin-1/2 adiabatic loop;
- Landau-level degeneracy and partial filling;
- variational hydrogenic energy;
- first Born scattering amplitude for a Gaussian potential;
- 1D Ising transfer-matrix thermodynamics;
- 3D spin-1/2 Fermi gas density factors;
- Abelian fractional quantum Hall K-matrix invariants.

Problem themes are drawn from public MIT OpenCourseWare quantum/statistical mechanics materials and standard topological condensed matter formulas. Numeric parameters are fixed benchmark variants.

## Run

Code use requested off:

```powershell
.\benchmarks\web-physics-adversarial-result-only-v0.1\run-kimi-adversarial-result-only.ps1 -NoCodeRequested
```

Code allowed/default:

```powershell
.\benchmarks\web-physics-adversarial-result-only-v0.1\run-kimi-adversarial-result-only.ps1
```

The default model alias is `kimi-code/kimi-for-coding`, displayed locally as `Kimi-k2.6`.

## Score

```text
hard_score = passed_final_fields / total_final_fields
```

This score does not certify derivation quality. The benchmark is meant to find final-answer failures and boundary-condition/sign mistakes quickly.
