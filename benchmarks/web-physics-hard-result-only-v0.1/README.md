# Web Physics Hard Result-Only Benchmark v0.1

Date: 2026-06-02

Purpose: harder initial baseline for Kimi Code + Kimi-k2.6 using public upper-division physics problem themes, scored only by final result fields.

## What Changed From The Easy Suite

The earlier OpenStax suite mostly tested one-step formula substitution. This suite targets upper-division quantum mechanics and solid-state style calculations:

- superposition in an infinite square well;
- above-barrier scattering at a potential step;
- finite rectangular barrier tunneling;
- attractive delta-function scattering;
- tight-binding group velocity and effective mass;
- identical-particle ground-state filling in a harmonic oscillator;
- bound-state transcendental equations for a finite square well.

The problem themes are aligned with public MIT OpenCourseWare 8.04 Quantum Physics I assignments and solutions, plus standard textbook quantum mechanics results. The numerical parameters here are fixed benchmark variants so the answer is obtained by solving the physics, not by copying a visible answer.

## Scope

- The verifier checks only final numerical values.
- Derivations, assumptions, source grounding, and reasoning quality are not scored.
- The run script copies only `prompt.md` into a temporary Kimi working directory.
- Gold values and verifier internals remain outside that directory.
- Network access is requested off but not technically enforced by this script.

## Run

```powershell
.\benchmarks\web-physics-hard-result-only-v0.1\run-kimi-hard-result-only.ps1
```

Default model alias:

```text
kimi-code/kimi-for-coding
```

In the local Kimi config this display name is `Kimi-k2.6`.

## Score

```text
hard_score = passed_final_fields / total_final_fields
```

This benchmark is intentionally result-only. A perfect score is not evidence of research-agent derivation discipline; it only shows the final numerical fields were correct within tolerance.
