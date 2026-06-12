# Open Physics Diverse Core-7

Answer all items. Return exactly one JSON object and no explanation.

Use these exact keys:

- `thermoqa_T1_SL_008_h_kJ_kg`
- `thermoqa_T1_SL_008_s_kJ_kgK`
- `thermoqa_T1_SL_008_v_m3_kg`
- `thermoqa_T1_SF_011_P_kPa`
- `thermoqa_T1_SF_011_h_kJ_kg`
- `thermoqa_T1_SF_011_s_kJ_kgK`
- `thermoqa_T1_SF_011_v_m3_kg`
- `cmphysbench_id4_commutator_x_px`
- `cmphysbench_id42_forced_oscillator_ground_energy`
- `cmt_hubbard_conserved_quantum_numbers`
- `cmt_dmrg_critical_bond_dimension_scaling`
- `cmt_qmc_average_sign_true_statements`

For numeric answers, return numbers only, with no units.
For symbolic answers, use compact LaTeX-like strings.
For multiple-answer questions, return a semicolon-separated lowercase choice set such as `"a;b;d"`.

## Problems

### 1. ThermoQA / compressed liquid water

Determine the specific enthalpy `h`, specific entropy `s`, and specific volume `v` of compressed liquid water at `T = 89 C` and `P = 10.4 MPa`.

Report:

- `h` in `kJ/kg`
- `s` in `kJ/(kg*K)`
- `v` in `m^3/kg`

### 2. ThermoQA / saturated liquid water

Determine the saturation pressure `P`, specific enthalpy `h`, specific entropy `s`, and specific volume `v` of saturated liquid water at `T = 147 C`.

Report:

- `P` in `kPa`
- `h` in `kJ/kg`
- `s` in `kJ/(kg*K)`
- `v` in `m^3/kg`

### 3. CMPhysBench / canonical commutator

Calculate the commutator `[x, p_x]`, where `x` is position and `p_x` is the momentum operator in the x-direction.

### 4. CMPhysBench / forced harmonic oscillator

A one-dimensional harmonic oscillator is subject to a uniform force `F`, so its potential is

`V(x) = (1/2) m omega^2 x^2 - F x`.

Find the ground-state energy.

### 5. CMT-Benchmark / one-band Hubbard model symmetries

Which quantum number or quantum numbers are conserved in the simple one-band Hubbard model?

Options:

- a. `U(1)` charge
- b. `SU(2)` spin
- c. `SU(2)` charge
- d. translation
- e. `U(1)` spin

### 6. CMT-Benchmark / DMRG critical chain scaling

DMRG represents a many-body wavefunction as a matrix product state with bond dimension `chi`. For a critical chain with entanglement entropy `S(l) = a log(l) + b`, what bond dimension is needed to represent a system of length `L = 2^n`?

Options:

- a. `log n`
- b. `n`
- c. `n^a`
- d. `2^(a n)`
- e. `a n`

### 7. CMT-Benchmark / QMC average sign

Which statements are true of the average sign in fermionic path-integral quantum Monte Carlo?

Options:

- a. The average sign is a property of a QMC algorithm.
- b. The average sign is a property of a path-integral representation of the physical problem.
- c. In a fermionic path-integral formulation, the average sign is always equal to zero.
- d. A negative sign may appear in the Monte Carlo weight because the Boltzmann distribution can be negative for some fermionic problems.
- e. A negative sign may appear because fermionic basis states are not orthogonal.
- f. A negative sign may appear because the wave function of a fermion changes sign under exchange of particles.
- g. The average sign will increase exponentially with beta for any fermionic system.
- h. The average sign will increase linearly with beta for any fermionic system.
- i. If the average sign is much smaller than one, the QMC simulation will produce high-variance results.
