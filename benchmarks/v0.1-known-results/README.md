# Known-Result Physics Benchmark v0.1

Date: 2026-05-30
Purpose: establish a baseline for Kimi Code before modifying its agent behavior.

## Goal

Use known physics results as a hard, reproducible capability test for a research
agent. The primary score must come from machine-verifiable answers or
deterministic checkers. Human rubric scoring is allowed only as secondary
failure analysis.

## Baseline Policy

Run two baselines before any Kimi Code agent modification:

1. `kimi-vanilla`: Kimi Code with no project-specific benchmark scaffolding loaded
   beyond the task prompt and input files.
2. `kimi-project-default`: Kimi Code in this repository with normal project skills
   available.

Use `kimi-project-default` as the practical baseline for our future modified
agent. Keep `kimi-vanilla` as the lower-level reference for how much the project
environment itself helps.

## Anti-Leakage Policy

Follow `ANTI-LEAKAGE-POLICY.md`. A benchmark run is valid only if the agent
cannot access gold answers, previous outputs, verifier internals, or web search
unless the task explicitly allows them. Any forbidden search or network use
invalidates the run.

## Frozen Variables

Record these for every run:

- Kimi Code version: `kimi --version`
- Kimi executable: `Get-Command kimi`
- command line used
- working directory
- model alias if provided with `--model`
- task id and task revision
- prompt file checksum
- output file checksum
- wall-clock runtime
- whether web/network access was allowed
- whether project skills were loaded

Do not edit task prompts, gold files, or rubrics after a baseline run unless the
task revision is bumped.

## First Task Mix

The first slice should contain 5-10 tasks, balanced across:

- derivation reproduction from known theory;
- exact or numeric answer checks;
- paper-grounded claim extraction;
- physics sanity checks such as dimensions, limits, symmetry, or Hermiticity;
- uncertainty control and source grounding.

For v0.1, prefer small tasks with trusted gold answers over broad research
workflows.

## Scoring Summary

The benchmark has two score layers:

1. `hard_score`: primary score from deterministic checkers such as JSON schema,
   symbolic/numeric equivalence, unit checks, exact values, or tolerance-based
   numerical tests.
2. `diagnostic_profile`: secondary explanation from the detailed rubric and
   failure tags.

Only `hard_score` should be used as the ability criterion for comparing Kimi
Code, modified Kimi agents, or other agents.

Use the detailed shared rubric in
`rubrics/known-result-rubric-detailed-v0.2.yaml`, plus each task's local
`checklist.yaml`.

Primary dimensions:

- `output_contract`
- `final_result`
- `derivation_core`
- `assumptions_and_conventions`
- `physics_checks`
- `source_grounding`
- `uncertainty_and_claim_control`

The detailed aggregate score is useful for debugging, but it is not the primary
benchmark score because it depends on human judgment.

For benchmark-development runs, the score file must include:

- `hard_score` from deterministic verification;
- total score out of 100;
- points earned per dimension;
- points earned per subcriterion;
- failure tags;
- hard-cap checks, even if no cap applies.

If `hard_score` and the diagnostic rubric disagree, the hard score wins for
agent capability comparison. The diagnostic rubric should explain why.

## Derivation Framework

Derivation-heavy tasks should use the shared protocol in
`../../design/physics-derivation-framework/README.md`.

The key benchmark object is a `derivation_record`, which separates:

- physical premises;
- formal translations from physics to mathematics;
- assumptions, approximations, conventions, and their license status;
- strict derivation steps;
- verification checks;
- final answer fields.

This lets the same structure serve two roles:

1. agent design: constrain when Kimi or a modified agent may introduce
   assumptions and approximations;
2. benchmark design: score derivation discipline with deterministic checks
   rather than trusting free-form prose.

For early v0.1 tasks, a task-specific subset of `derivation_record` is allowed
if the verifier documents which fields are checked. New derivation tasks should
move toward the full schema in
`../../design/physics-derivation-framework/schemas/derivation-record.schema.json`.

Benchmark failure analysis should use the same framework. Deterministic
attribution may localize a failure to a failed check and upstream node. If that
does not uniquely identify the cause, the benchmark should generate or select
probe tests rather than relying on a subjective explanation. The shared schemas
are:

- `../../design/physics-derivation-framework/schemas/failure-attribution.schema.json`
- `../../design/physics-derivation-framework/schemas/probe-test.schema.json`

## Run Layout

Store each run as:

```text
runs/
  <date>__<agent>__<run_id>/
    run-metadata.yaml
    outputs/
      <task_id>.md
    scores/
      <task_id>.score.yaml
    logs/
      <task_id>.stdout.txt
      <task_id>.stderr.txt
```

Never overwrite a run directory. If a task or rubric changes, create a new
benchmark revision.

## Kimi Command Pattern

Project-default baseline:

```powershell
kimi -p (Get-Content -Raw benchmarks/v0.1-known-results/tasks/<task_id>/prompt.md) `
  --output-format text
```

Vanilla baseline should use an explicit empty skills directory once confirmed:

```powershell
kimi --skills-dir <empty-skills-dir> `
  -p (Get-Content -Raw benchmarks/v0.1-known-results/tasks/<task_id>/prompt.md) `
  --output-format text
```

If Kimi still auto-loads user or project context despite `--skills-dir`, record
that behavior in `run-metadata.yaml` instead of silently treating it as vanilla.

## Modification Rule

After the baseline is frozen, modify only the agent/harness under experiment.
Do not tune the benchmark to fit the modified agent unless the benchmark moves
to a new version.
