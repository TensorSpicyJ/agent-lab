# SciBench Physics Mixed 8

Use only the final numeric result for each problem. Do not explain. Return exactly one JSON object:

```json
{
  "answers": {
    "class_2_6_big_bertha_range_km": 0,
    "class_7_10_hemisphere_leave_angle_deg": 0,
    "class_8_5_hohmann_transfer_time_1e7_s": 0,
    "matter_4_1_photoelectric_lambda_max_nm": 0,
    "matter_17_1_hydrogenic_heplus_energy_ev": 0,
    "matter_37_4_thermal_neutron_wavelength_pm": 0,
    "quan_1_6_1_b_position_probability": 0,
    "quan_6_6_1_hydrogen_ground_energy_ev": 0
  }
}
```

Problems copied from SciBench public dataset pages:

1. `class / problemid 2.6`
We treat projectile motion in two dimensions, first without considering air resistance. Let the muzzle velocity of the projectile be $v_0$ and the angle of elevation be $\theta$. The Germans used a long-range gun named Big Bertha in World War I to bombard Paris. Its muzzle velocity was $1,450 \mathrm{~m} / \mathrm{s}$. Find its predicted range of flight if $\theta=55^{\circ}$.
Answer unit: `km`

2. `class / problemid 7.10`
A particle of mass $m$ starts at rest on top of a smooth fixed hemisphere of radius $a$. Determine the angle at which the particle leaves the hemisphere.
Answer unit: `deg`

3. `class / problemid 8.5`
Calculate the time needed for a spacecraft to make a Hohmann transfer from Earth to Mars.
Answer unit: `10^7 s`

4. `matter / problemid 4.1`
Calculating the maximum wavelength capable of photoejection. A photon of radiation of wavelength $305 \mathrm{~nm}$ ejects an electron from a metal with a kinetic energy of $1.77 \mathrm{eV}$. Calculate the maximum wavelength of radiation capable of ejecting an electron from the metal.
Answer unit: `nm`

5. `matter / problemid 17.1`
The single electron in a certain excited state of a hydrogenic $\mathrm{He}^{+}$ ion $(Z=2)$ is described by the wavefunction $R_{3,2}(r) \times Y_{2,-1}(\theta, \phi)$. What is the energy of its electron?
Answer unit: `eV`

6. `matter / problemid 37.4`
Calculate the typical wavelength of neutrons after reaching thermal equilibrium with their surroundings at $373 \mathrm{~K}$. For simplicity, assume that the particles are travelling in one dimension.
Answer unit: `pm`

7. `quan / problemid 1.6.1_b`
A one-particle, one-dimensional system has $\Psi=a^{-1 / 2} e^{-|x| / a}$ at $t=0$, where $a=1.0000 \mathrm{~nm}$. At $t=0$, the particle's position is measured. Find the probability that the measured value is between $x=0$ and $x=2 \mathrm{~nm}$.
Answer unit: dimensionless

8. `quan / problemid 6.6.1`
Calculate the ground-state energy of the hydrogen atom using SI units and convert the result to electronvolts.
Answer unit: `eV`
