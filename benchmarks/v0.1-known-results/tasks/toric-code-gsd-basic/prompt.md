# Task: Toric Code Ground-State Degeneracy on a Torus

You are given a known result from the toric code: on a torus, the ground-state
degeneracy is 4.

Reconstruct the argument in a compact but rigorous way.

Requirements:

1. State the final result.
2. Explain which assumptions are being used.
3. Give the derivation logic, not just the answer.
4. Include at least two physics sanity checks or consistency checks.
5. Mark any step that depends on a convention or unstated theorem.
6. Do not claim novelty.

Output format:

```markdown
## Final Result

## Assumptions

## Derivation

## Physics Checks

## Uncertainty / Caveats
```

At the end, include a machine-gradable JSON block exactly in this shape:

```json
{
  "task_id": "toric-code-gsd-basic",
  "final_gsd": 4,
  "encoded_qubits": 2,
  "surface": "torus",
  "assumptions": [
    "closed torus / periodic boundary conditions",
    "standard toric code with qubits on edges",
    "commuting star and plaquette stabilizers",
    "ground states are simultaneous +1 stabilizer eigenspaces"
  ],
  "stabilizer_counting": {
    "qubits_on_edges": true,
    "star_global_redundancy": true,
    "plaquette_global_redundancy": true,
    "independent_stabilizers": "V + F - 2",
    "euler_characteristic": "V - E + F = 0",
    "logical_qubits_formula": "E - (V + F - 2) = 2"
  },
  "checks": {
    "sphere_gsd": 1,
    "genus_formula": "4^g",
    "logical_loop_algebra": true
  },
  "caveats": {
    "no_novelty_claim": true,
    "ideal_commuting_projector_exact": true,
    "perturbative_splitting_exponential": true
  }
}
```
