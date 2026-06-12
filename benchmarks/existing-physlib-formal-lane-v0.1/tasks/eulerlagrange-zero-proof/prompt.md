# Euler-Lagrange Zero Proof

Fill only the Lean proof body after `by`.

Do not repeat the theorem statement. Do not add explanations. Output one Lean code block only.

```lean
import Physlib.ClassicalMechanics.EulerLagrange

open ClassicalMechanics
open Time
open InnerProductSpace

example {X} [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X] (q : Time → X) :
    eulerLagrangeOp (fun _ _ _ => 0) q = fun _ => 0 := by
  -- fill proof here
```
