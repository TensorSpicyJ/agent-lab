# TPBench Public Mini 3

Solve the following public TPBench problems. Return exactly one Python code block defining all three required functions:

```python
def answer() -> float:
    pass

def speed(v_e: float, delta_v: float) -> float:
    pass

def expectation_value(A: float, E_a: float, E_b: float, t: float) -> float:
    pass
```

Do not print anything. Do not include explanations.

## Problem 1: Blackbody in d Dimensions

Source: TPBench public problem, difficulty level 1.

Assume we live in a 4+1 dimensional spacetime. How does the total energy density of a black body scale with temperature T. Find the exponent n in the expression u proportional to T^n.

Answer requirement:

```python
def answer() -> float:
    pass
```

## Problem 2: Boosted Parabolic Trajectory

Source: TPBench public problem, difficulty level 1.

Consider a situation where a space-probe very briefly fires its rockets while passing a planet of mass M at periapsis, its nearest point to the planet. Suppose that the probe is on a parabolic trajectory and at periapsis, when travelling at velocity v_e, it results in a boost of delta_v. What will be its speed once it escapes the planet's gravitational field only in terms of v_e and delta_v?

Answer requirement:

```python
def speed(v_e: float, delta_v: float) -> float:
    pass
```

## Problem 3: A 3-State QM Problem

Source: TPBench public problem, difficulty level 2.

The Hamiltonian of a three-level system is

```text
H = [[E_a, 0, A],
     [0, E_b, 0],
     [A, 0, E_a]]
```

where A is real. The state of the system at time t = 0 is, in this basis,

```text
psi(0) = (1 / sqrt(2)) * [1, 1, 0]^T
```

What is the expectation value of the energy at time t?

Answer requirement:

```python
def expectation_value(A: float, E_a: float, E_b: float, t: float) -> float:
    pass
```
