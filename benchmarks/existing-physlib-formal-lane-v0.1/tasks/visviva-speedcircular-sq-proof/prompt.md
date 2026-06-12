# Vis Viva Speed Squared Proof

Fill only the Lean proof body after `by`.

Do not repeat the theorem statement. Do not add explanations. Output one Lean code block only.

```lean
import Physlib.ClassicalMechanics.OrbitalMechanics.VisViva

open ClassicalMechanics

example (sys : VisViva.VisViva) (cfg : VisViva.ConfigurationSpace)
    (hr : 0 < cfg.r) (hG : 0 < sys.G) (hM : 0 < sys.M) :
    (VisViva.speedCircular sys cfg)^2 = sys.G * sys.M / cfg.r := by
  -- fill proof here
```
