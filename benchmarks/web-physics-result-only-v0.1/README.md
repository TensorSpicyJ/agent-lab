# Web Physics Result-Only Benchmark v0.1

Date: 2026-06-02

Purpose: quick initial baseline for Kimi Code + Kimi-k2.6 on public, textbook-style physics problems, scored only by final numerical results.

## Scope

This benchmark is deliberately shallow:

- The task set is adapted from publicly accessible OpenStax examples.
- The model sees only the problem statements and a strict JSON output contract.
- The verifier ignores derivation quality and checks only final numerical fields.
- The run is file-isolated into a temporary directory containing only `prompt.md`.
- Network use is requested to be off, but not technically enforced by this script.

Use this as a first-pass sanity baseline, not as evidence of research-agent reasoning discipline.

## Task

`tasks/openstax-result-only-suite/prompt.md` contains one suite with 17 numerical answer fields across mechanics, work-energy, electrostatics, and Ohm's law.

Gold values are stored in `tasks/openstax-result-only-suite/private/gold.json` and are not copied into the temporary Kimi working directory.

## Run

```powershell
.\benchmarks\web-physics-result-only-v0.1\run-kimi-openstax-result-only.ps1
```

Default model alias:

```text
kimi-code/kimi-for-coding
```

In the local Kimi config this display name is `Kimi-k2.6`.

## Score

The primary metric is:

```text
hard_score = passed_numeric_fields / total_numeric_fields
```

The verifier accepts small tolerance windows around the published or recomputed textbook results. It does not award or subtract points for explanation.
