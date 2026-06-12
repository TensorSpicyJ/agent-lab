import Physlib.ClassicalMechanics.EulerLagrange

open ClassicalMechanics
open Time
open InnerProductSpace

example {X} [NormedAddCommGroup X] [InnerProductSpace ℝ X] [CompleteSpace X] (q : Time → X) :
    eulerLagrangeOp (fun _ _ _ => 0) q = fun _ => 0 := by
{{PROOF}}
