# Adversarial Result-Only Physics Benchmark

Solve the following higher-level physics problems. Return only the final JSON object requested below.

Rules:
- Do not browse the web or search for answers.
- Do not ask follow-up questions.
- Report numbers with enough precision to pass a tolerance-based checker.
- Use the conventions and units stated in each problem.

## Problems

1. Degenerate perturbation theory. In the basis `|1>, |2>, |3>`,
   `H0 = diag(0, 0, 3)` and `H = H0 + eps V`, with
   `V = [[1, 2, 1], [2, 1, -1], [1, -1, 0]]`.
   For the two states that descend from the degenerate `E=0` subspace, report the larger and smaller first-order energy shifts, and their second-order energy shifts from coupling to `|3>`.

2. Berry phase. A spin-1/2 state with `sigma dot n` eigenvalue `+1` adiabatically follows a magnetic-field direction around one closed cone at fixed polar angle `theta = pi/3`. With the usual Berry-phase sign convention for this eigenstate, report the solid angle divided by `pi`, the Berry phase divided by `pi`, and the cosine and sine of the Berry phase.

3. Landau filling. Spinless electrons in 2D have `hbar = m = |q| = B = 1` and area `A = 20 pi`. Energies are `E_n = n + 1/2`. Fill `N = 23` electrons at zero temperature. Report the degeneracy per Landau level, the total ground-state energy, the highest occupied Landau index, and the filling fraction of that highest level.

4. Variational hydrogenic trial state. In atomic units, use the normalized trial state `psi_alpha(r) = (alpha^3/pi)^(1/2) exp(-alpha r)` for a Coulomb potential with `Z = 2`. Report the optimal `alpha`, the optimal variational energy, and the variational energy at `alpha = 1.5`.

5. First Born approximation. For a 3D Gaussian potential `V(r) = V0 exp(-r^2/a^2)` with `V0 = 0.8`, `a = 1.2`, incoming wave number `k = 1.5`, and scattering angle `theta = pi/3`, use units with `2m/hbar^2 = 1`. Report the momentum transfer `q`, the Born scattering amplitude `f(theta)`, and `d sigma / d Omega`.

6. One-dimensional Ising transfer matrix. For the classical 1D Ising model with coupling `J = 0.7`, field `h = 0.2`, and `beta = 1`, report the two transfer-matrix eigenvalues `lambda_plus` and `lambda_minus`, the thermodynamic-limit free energy per spin, magnetization per spin, and correlation length.

7. Three-dimensional spin-1/2 free Fermi gas. In units with `hbar^2/(2m)=1`, total number density including both spin species is `n = 0.05`. At zero temperature, report `k_F`, `E_F`, average energy per particle, and pressure.

8. Abelian FQH K-matrix. For
   `K = [[3, 1], [1, 3]]`, charge vector `t = (1, 1)`, and quasiparticle vector `l = (1, 0)`, use the standard Abelian K-matrix formulas. Report torus ground-state degeneracy, genus-2 ground-state degeneracy, filling fraction, quasiparticle charge, and exchange statistics `theta/pi`.

## Output Contract

Return exactly one JSON object. No Markdown fence and no explanation.

```json
{
  "benchmark_id": "web-physics-adversarial-result-only-v0.1",
  "task_id": "adversarial-physics-result-only-suite",
  "answers": {
    "deg_pt_large_first_order": 0,
    "deg_pt_small_first_order": 0,
    "deg_pt_large_second_order": 0,
    "deg_pt_small_second_order": 0,
    "berry_solid_angle_over_pi": 0,
    "berry_phase_over_pi": 0,
    "berry_phase_cos": 0,
    "berry_phase_sin": 0,
    "landau_degeneracy": 0,
    "landau_ground_energy": 0,
    "landau_highest_occupied_n": 0,
    "landau_top_level_filling": 0,
    "var_alpha_opt": 0,
    "var_energy_opt": 0,
    "var_energy_alpha_1p5": 0,
    "born_q": 0,
    "born_f": 0,
    "born_dsigma_domega": 0,
    "ising_lambda_plus": 0,
    "ising_lambda_minus": 0,
    "ising_free_energy_per_spin": 0,
    "ising_magnetization": 0,
    "ising_correlation_length": 0,
    "fermi_kF": 0,
    "fermi_EF": 0,
    "fermi_avg_energy": 0,
    "fermi_pressure": 0,
    "kmatrix_torus_gsd": 0,
    "kmatrix_genus2_gsd": 0,
    "kmatrix_filling_fraction": 0,
    "kmatrix_quasiparticle_charge": 0,
    "kmatrix_exchange_theta_over_pi": 0
  }
}
```
