# Result-Only Physics Benchmark: OpenStax Suite

Solve the following public textbook-style physics problems. Return only the final JSON object requested below.

Rules:
- Do not browse the web or search for answers.
- Do not ask follow-up questions.
- You may do scratch reasoning internally, but do not include derivations in the output.
- Report numbers in the units specified by each JSON key.
- Use `g = 9.8 m/s^2` when needed.

## Problems

1. A 30.0 kg package moves at 0.500 m/s. Find its kinetic energy.

2. The same package is pushed by a constant 120 N force over 0.800 m, while friction averages 5.00 N opposite the motion. Its initial kinetic energy is 3.75 J. Find its final speed.

3. An 80 kg athlete runs at 10 m/s. Find the athlete's kinetic energy.

4. An asteroid traveling at 22 km/s releases `4.2e23 J` of kinetic energy on impact. Find its mass.

5. A thermal neutron of mass `1.68e-27 kg` travels at 2.2 km/s. Find its kinetic energy.

6. A fireworks shell is launched at 70.0 m/s and 75 degrees above the horizontal. At the highest point, find the height above launch, time from launch, and horizontal displacement.

7. A tennis ball is hit at 30 m/s and 45 degrees above the horizontal, then caught 10 m above its launch height on the way down. Find the longer flight time to the catch, the impact speed, and the impact angle below the horizontal.

8. A golf ball must travel 90 m on level ground. Find the required launch speed for a 30 degree shot and for a 70 degree shot.

9. Compare an electron and proton separated by `0.530e-10 m`. Using `k = 8.99e9 N m^2/C^2`, `e = 1.60e-19 C`, `G = 6.67e-11 N m^2/kg^2`, `m_e = 9.11e-31 kg`, and `m_p = 1.67e-27 kg`, find the Coulomb force magnitude, gravitational force magnitude, and Coulomb/gravity force ratio.

10. An automobile headlight has 2.50 A of current when 12.0 V is applied. Find its resistance.

## Output Contract

Return exactly one JSON object. No Markdown fence and no explanation.

```json
{
  "benchmark_id": "web-physics-result-only-v0.1",
  "task_id": "openstax-result-only-suite",
  "answers": {
    "package_ke_j": 0,
    "package_final_speed_m_s": 0,
    "athlete_ke_j": 0,
    "asteroid_mass_kg": 0,
    "thermal_neutron_ke_j": 0,
    "firework_max_height_m": 0,
    "firework_apex_time_s": 0,
    "firework_apex_x_m": 0,
    "tennis_time_s": 0,
    "tennis_impact_speed_m_s": 0,
    "tennis_impact_angle_deg_below_horizontal": 0,
    "golf_30deg_speed_m_s": 0,
    "golf_70deg_speed_m_s": 0,
    "coulomb_force_n": 0,
    "gravity_force_n": 0,
    "coulomb_gravity_ratio": 0,
    "headlight_resistance_ohm": 0
  }
}
```
