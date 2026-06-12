# Hard Result-Only Physics Benchmark: Quantum Mechanics Suite

Solve the following upper-division physics problems. Return only the final JSON object requested below.

Rules:
- Do not browse the web or search for answers.
- Do not ask follow-up questions.
- You may do scratch reasoning internally, but do not include derivations in the output.
- Use the dimensionless units and conventions stated in each problem.
- Report numbers with enough precision to pass a tolerance-based checker.

## Problems

1. Infinite square well. A particle is in a 1D infinite well `0 < x < L`. At `t = 0`,
   `psi(x,0) = A [sin(pi x/L) + sqrt(2) sin(2 pi x/L) + sqrt(3) sin(3 pi x/L)]`.
   Energies are `E_n = n^2 E1`. Find the probabilities for measuring `E1`, `4 E1`, and `9 E1`, plus `<E>/E1` and `Var(E)/E1^2`.

2. Potential step scattering. A particle with energy `E = 4 V0` comes from the left toward a step `V(x)=0` for `x<0` and `V0` for `x>0`. With real wave numbers and incident amplitude 1, find the reflection amplitude `r`, transmission amplitude `t`, reflection probability `R`, and flux transmission probability `T`.

3. Rectangular barrier tunneling. A particle with `E/V0 = 0.5` crosses a barrier of width `a`. Let `gamma0 = a sqrt(2m V0)/hbar = 3.0`. Use the exact below-barrier formula
   `T = 1 / [1 + sinh(gamma0 sqrt(1 - E/V0))^2 / (4 (E/V0)(1 - E/V0))]`.
   Also compute the thick-barrier approximation `T_approx = 16 e (1-e) exp[-2 gamma0 sqrt(1-e)]`, where `e = E/V0`.

4. Attractive delta potential scattering. A particle with wave number `k` scatters from `V(x) = -lambda delta(x)`. Let `gamma = m lambda/(hbar^2 k) = 2.5`. Using `t = 1/(1 - i gamma)`, report `Re(t)`, `Im(t)`, `T = |t|^2`, and `R`.

5. Tight-binding band. In units with `E(k) = -2 cos(ka)`, `hbar = 1`, and lattice spacing `a = 1`, compute group velocity `v_g = dE/dk`, inverse effective mass `d^2E/dk^2`, and effective mass `m* = 1/(d^2E/dk^2)` at `k = pi/3` and at `k = 2pi/3`.

6. Identical particles in a 1D harmonic oscillator. In units of `hbar omega`, six spinless identical particles occupy oscillator levels with single-particle energies `epsilon_n = n + 1/2` for `n = 0,1,2,...`.
   Find the ground-state energy and first excitation gap for six spinless fermions, and the ground-state energy and first excitation gap for six spinless bosons.

7. Finite square well bound states. For an even finite well with width `2a`, depth `V0`, and dimensionless strength `z0 = a sqrt(2m V0)/hbar = 3.0`, define `z = k a` and `energy_ratio = E/V0`, where bound energies are negative relative to the outside zero. The even states solve `z tan z = sqrt(z0^2 - z^2)`, and odd states solve `-z cot z = sqrt(z0^2 - z^2)`. Report the number of bound states, the first even-state `z`, the first odd-state `z`, and their `energy_ratio = z^2/z0^2 - 1`.

## Output Contract

Return exactly one JSON object. No Markdown fence and no explanation.

```json
{
  "benchmark_id": "web-physics-hard-result-only-v0.1",
  "task_id": "quantum-hard-result-only-suite",
  "answers": {
    "well_prob_E1": 0,
    "well_prob_4E1": 0,
    "well_prob_9E1": 0,
    "well_mean_E_over_E1": 0,
    "well_var_E_over_E1_sq": 0,
    "step_r": 0,
    "step_t": 0,
    "step_R": 0,
    "step_T": 0,
    "barrier_T_exact": 0,
    "barrier_T_thick_approx": 0,
    "delta_t_re": 0,
    "delta_t_im": 0,
    "delta_T": 0,
    "delta_R": 0,
    "band_pi3_vg": 0,
    "band_pi3_inv_mass": 0,
    "band_pi3_m_star": 0,
    "band_2pi3_vg": 0,
    "band_2pi3_inv_mass": 0,
    "band_2pi3_m_star": 0,
    "fermion_ground_E_over_hw": 0,
    "fermion_first_gap_over_hw": 0,
    "boson_ground_E_over_hw": 0,
    "boson_first_gap_over_hw": 0,
    "finite_well_bound_state_count": 0,
    "finite_well_even0_z": 0,
    "finite_well_odd0_z": 0,
    "finite_well_even0_energy_ratio": 0,
    "finite_well_odd0_energy_ratio": 0
  }
}
```
