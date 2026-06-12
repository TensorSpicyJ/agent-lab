# PhysLib Local Scan 2026-06-02

Repository inspected locally:
- `HEPLean/PhysLean`

README note:
- the repository reports a recent rename/move to `leanprover-community/physlib`

Lean file counts:

| Area | Lean files |
| --- | ---: |
| Relativity | 81 |
| QFT | 72 |
| Particles | 64 |
| QuantumMechanics | 37 |
| Electromagnetism | 34 |
| Mathematics | 34 |
| SpaceAndTime | 35 |
| ClassicalMechanics | 21 |
| Meta | 16 |
| Units | 14 |
| StringTheory | 13 |
| StatisticalMechanics | 8 |
| FluidDynamics | 4 |
| Thermodynamics | 4 |
| CondensedMatter | 2 |
| Cosmology | 2 |
| Optics | 2 |
| ClassicalFieldTheory | 1 |
| Total `Physlib/*.lean` | 444 |
| Total `QuantumInfo/*.lean` | 84 |

Interpretation:
- This is already a large formal physics corpus.
- It is much richer in relativity, QFT, particles, and quantum mechanics than the current local benchmark suite.
- Condensed matter and optics exist but are still comparatively thin.
- For the user's benchmark program, the most realistic next formal lane is a small Lean4 subset from:
  - classical mechanics
  - electromagnetism
  - quantum mechanics
  - thermodynamics
