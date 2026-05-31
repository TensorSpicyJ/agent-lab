# Physics Derivation Framework

Date: 2026-05-30

Purpose: define a shared intermediate representation for physics derivation
agents and physics derivation benchmarks.

This framework is meant to be used in two places:

1. Agent design: constrain when an agent may introduce physical assumptions,
   approximations, conventions, and model translations.
2. Benchmark design: require the same objects as machine-checkable outputs, so
   the benchmark can score derivation discipline instead of only final answers.

## Core Claim

Physics derivations should be split into four layers:

1. Physical premise layer: regimes, approximations, effective theories,
   boundary conditions, neglected terms, empirical inputs.
2. Formal translation layer: mapping physical objects into mathematical
   objects, such as Hamiltonians, K matrices, Hilbert spaces, symmetry groups,
   order parameters, and observables.
3. Strict derivation layer: algebra, topology, calculus, variational steps,
   counting arguments, symbolic transformations, or proof-assistant steps under
   fixed definitions and premises.
4. Physical interpretation layer: mapping mathematical results back to
   observables, phases, materials, or experimental statements.

Only layer 3 is strict by default. Layers 1, 2, and 4 must be made explicit and
auditable before layer 3 can be trusted.

## Shared Output Object

Every derivation-capable agent should be able to emit a `derivation_record`:

```json
{
  "task_id": "example-task",
  "claim": "target statement",
  "physical_premises": [],
  "formal_translations": [],
  "assumption_ledger": [],
  "derivation_trace": [],
  "verification_checks": [],
  "final_answer": {}
}
```

Benchmarks should grade this object directly. Agent implementations may keep it
as internal state and expose it only at checkpoints.

For small benchmark tasks, use the compact answer-card protocol in
`ANSWER-CARD-PROTOCOL.md`. The agent emits a short `answer_card`; the harness
can expand it into a full `derivation_record` for archival and attribution.
This avoids turning output length and JSON boilerplate into the benchmark's
main difficulty.

## Assumption Ledger

The `assumption_ledger` is the gate between physical intuition and derivation.
An agent may propose an assumption or approximation, but it should not use it as
a derivation premise unless it is licensed.

Each entry should answer:

- What is being assumed or approximated?
- Which regime or small/large parameter supports it?
- Where did the support come from: prompt, source excerpt, prior theorem, user
  instruction, or explicit modeling choice?
- What is the error order or validity boundary, if applicable?
- Which symmetries, conservation laws, limits, or dimensions must remain valid?
- Is the assumption licensed, conditional, rejected, or unresolved?

Status meanings:

| Status | Meaning |
| --- | --- |
| `licensed` | May be used as a premise in the derivation. |
| `conditional` | May only be used inside an explicit if-assumption branch. |
| `rejected` | Must not be used. |
| `unresolved` | Requires more source information, user input, or verification. |

## Approximation Gate

An approximation may be licensed only if it passes all applicable checks:

1. Regime is explicit or the answer is explicitly conditional.
2. Small or large parameter is identified.
3. Error order or validity boundary is stated when the approximation is an
   expansion.
4. Dimensional consistency is preserved.
5. Relevant symmetries, conservation laws, constraints, and gauge conventions
   are preserved or explicitly broken by the premise.
6. Known-limit or special-case checks do not contradict the approximation.

If any required check fails, the agent should not continue as if the
approximation were true. It should either reject the step or branch:

```text
If assumption A is added, result R follows. Without A, R is not determined by
the provided premises.
```

## Formal Translation Layer

The translation layer prevents hidden model choices from being treated as
derivation steps.

Examples:

- Physical FQH state -> Abelian K-matrix Chern-Simons model.
- Lattice spin model -> stabilizer Hamiltonian on a torus.
- Low-energy band edge -> effective quadratic dispersion.
- Experimental peak position -> lattice constant or strain estimate.

Every translation should identify:

- source physical object;
- target mathematical object;
- conventions, basis, gauge, topology, or boundary conditions;
- whether the mapping is given, inferred, standard, or speculative;
- what would invalidate the mapping.

## Derivation Trace

The derivation trace contains only strict or explicitly licensed steps.

Each step should include:

- stable step id;
- statement;
- rule from an allowed rule enum;
- dependencies on source excerpts, translations, assumptions, or prior steps;
- optional machine expression for CAS/proof-assistant checking.

The verifier should check:

- required steps are present;
- rules are allowed;
- dependencies form an acyclic graph;
- no derivation step depends on a rejected or unresolved assumption;
- formulas normalize to the expected result or pass generated hidden cases.

## Failure Attribution

Benchmark attribution should be strict where possible and test-driven where it
is not.

Strict attribution means localizing a failure to a failed check, field, and
upstream node in the `derivation_record`. It does not mean claiming to know the
agent's internal psychological reason.

Allowed attribution modes:

| Mode | Meaning |
| --- | --- |
| `deterministic_single_cause` | One upstream node uniquely violates a rule. |
| `deterministic_multi_candidate` | The verifier can narrow the issue to several candidate nodes but cannot distinguish them from this task alone. |
| `diagnostic_only` | The explanation is useful for humans but is not a hard benchmark finding. |

When attribution is not uniquely strict, the benchmark should add probe tests
instead of pretending the root cause is known. A probe test is a small controlled
variant designed to distinguish candidate causes.

Example:

```text
Observed failure: the agent used K' = W K W^T.
Task convention: K' = W^T K W.

Strict localization:
  formal translation node T1 violates the source convention.

Not strictly known from one task:
  whether the model ignored the source, used a memorized alternate convention,
  or made a one-off algebra slip.

Probe:
  provide a new source excerpt that explicitly reverses the convention and use
  matrices where the two conventions differ. If the agent follows the new
  source, source reading is likely intact; if it keeps the old convention, the
  issue is source-grounding or instruction-following.
```

The machine-readable schemas are:

- `schemas/failure-attribution.schema.json`
- `schemas/probe-test.schema.json`
- `schemas/reasoning-assisted-attribution.schema.json`

Reasoning-assisted attribution may use Kimi-style `reasoning_content`, stderr
thinking logs, or scratchpads to diagnose why a hard failure occurred. It must
remain diagnostic-only. The hard score is still determined by final structured
output and deterministic verifiers.

## Agent Runtime Design

A physics derivation agent should split roles internally:

1. `premise_extractor`: reads prompt/source and extracts explicit regimes,
   definitions, inputs, and constraints.
2. `translation_builder`: converts physical statements to formal objects and
   records conventions.
3. `assumption_proposer`: proposes assumptions or approximations when needed.
4. `approximation_gate`: licenses, rejects, or branches assumptions using the
   ledger checks.
5. `deriver`: performs only steps whose dependencies are source facts,
   translations, licensed assumptions, or previous derivation steps.
6. `verifier`: checks algebra, dimensions, known limits, symmetries, and output
   schema.

The important separation is that the same model may propose assumptions, but
the runtime must force an explicit gate before those assumptions become usable.

## Benchmark Design

A benchmark task should specify:

- visible prompt and source packet;
- expected `derivation_record` fields;
- allowed assumptions and forbidden assumptions, where applicable;
- allowed derivation rules;
- required checks;
- hidden generated instances for final-answer or formula validation;
- hard verifier behavior.

Task families should include:

1. Explicit-regime tasks: the needed approximation is licensed by the prompt.
2. Missing-regime tasks: the correct answer must refuse or branch.
3. Invalid-assumption traps: a common approximation is tempting but invalid.
4. Translation traps: the math is easy if, and only if, the model translation is
   chosen correctly.
5. Strict-core tasks: the physical premise is fixed and the benchmark checks
   pure derivation quality.

## Relationship To Lean

The framework does not require every task to be a Lean proof. Instead it creates
a path:

1. structured derivation record;
2. deterministic JSON/schema checks;
3. symbolic or numeric verifier;
4. CAS equivalence checks;
5. proof-assistant formalization for narrow exact cores.

For topological order tasks, good Lean/CAS targets include integer matrices,
unimodular basis changes, determinants, quotient lattices, Smith normal form,
and stabilizer-code counting. The physical claim that a real material or phase
is described by a particular effective theory remains a premise unless separately
justified.
