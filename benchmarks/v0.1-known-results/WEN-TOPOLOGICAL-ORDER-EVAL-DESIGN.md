# Wen Topological Order Eval Design

Date: 2026-05-30

## Target Source

Primary candidate:

- Xiao-Gang Wen, "Topological orders and Edge excitations in FQH states"
  arXiv:cond-mat/9506066, Advances in Physics 44, 405 (1995).

This paper is a good benchmark source because it connects bulk topological order
to experimentally visible edge structures, and many outputs can be made
machine-checkable.

## Key Principle

Do not ask the agent to summarize Wen's paper. Build tasks where the agent must
read a controlled source packet and produce structured answers that a verifier
can check.

The task should test:

- extraction from source text;
- correct use of the K-matrix / edge theory formalism;
- computation of topological invariants;
- correct mapping between bulk data and edge/quasiparticle data;
- avoidance of unsupported claims.

## Computation vs Derivation

The first `wen-kmatrix-laughlin-hidden-m` task tests formula application. It is
not enough to prove derivation ability.

To test derivation ability, the benchmark must require a checkable derivation
object, not only final values.

Use the shared protocol in
`../../design/physics-derivation-framework/README.md` for new derivation tasks.
For Wen/K-matrix tasks this means the benchmark should distinguish:

- the physical premise that a phase is represented by an Abelian K-matrix
  effective theory;
- the formal translation to integer matrices, charge vectors, quotient
  lattices, and unimodular basis changes;
- strict algebraic or lattice derivation steps;
- the physical interpretation of the resulting invariant.

### Derivation Capability Target

The agent must show it can transform premises into the target formula through
valid intermediate statements.

For K-matrix tasks, useful derivation targets include:

- derive `GSD_torus = |det K|` from equivalence classes of integer
  quasiparticle vectors modulo local particles;
- derive `GSD_genus_g = |det K|^g` from independent non-contractible cycles;
- derive `q_l = t^T K^{-1} l` from coupling to the electromagnetic response;
- derive exchange statistics `theta_l/pi = l^T K^{-1} l`;
- derive invariance of `nu = t^T K^{-1}t` under a unimodular basis transform.

### Machine-Checkable Derivation Format

Require the agent to output a structured derivation trace:

```json
{
  "derivation_claim": "GSD_torus = |det K|",
  "steps": [
    {
      "id": "S1",
      "statement": "anyon_lattice = Z^N / K Z^N",
      "rule": "local_particle_quotient",
      "depends_on": ["source:K-matrix local particles"]
    },
    {
      "id": "S2",
      "statement": "|Z^N / K Z^N| = |det K|",
      "rule": "smith_normal_form",
      "depends_on": ["S1"]
    },
    {
      "id": "S3",
      "statement": "GSD_torus = |det K|",
      "rule": "torus_sector_count",
      "depends_on": ["S2"]
    }
  ],
  "final_formula": "|det K|"
}
```

The verifier should check:

- required steps are present;
- each step's `rule` is from an allowed rule enum;
- dependencies form a DAG ending in the target formula;
- algebraic formulas are equivalent after normalization;
- the final formula evaluates correctly on hidden test matrices.

This does not fully prove the derivation like Lean would, but it is much harder
to fake than free-form prose.

### Stronger Option: Symbolic / CAS Checks

For basis-transform derivations, the verifier can check symbolic identities:

```text
K' = W^T K W
t' = W^T t
nu' = t'^T (K')^{-1} t'
nu' == t^T K^{-1} t
```

Use random unimodular integer matrices `W` and multiple generated `K` matrices.
If the derivation is wrong but the final answer is guessed, hidden variants will
usually expose it.

## How To Choose Source Excerpts

An excerpt is allowed if it teaches the method but does not reveal the generated
instance answer.

Use this three-way split:

| Excerpt type | Include? | Reason |
| --- | --- | --- |
| Formalism definition | Yes | Needed to solve the task: K matrix, charge vector, edge fields, quasiparticle vector |
| General formula | Usually yes | It teaches the method, e.g. `nu = t^T K^{-1} t`, `GSD = |det K|^g` |
| Worked example with same parameters | No | It leaks the answer |
| Table of canonical states | Avoid or redact | It can let the agent match by lookup |
| Conceptual motivation | Optional | Useful for reading tasks, weak for hard-score tasks |
| Historical claims / broad review text | Usually no | Not needed for hard scoring and increases noise |
| Equation plus local explanation | Yes | Best source excerpt unit |
| Long surrounding pages | Avoid | More leakage and harder source-span verification |

### Selection Procedure

1. Identify the target capability.
   - Example: compute filling fraction, edge chirality, or quasiparticle
     statistics.
2. Extract only the minimal paragraph/equation block that defines the method.
3. Remove worked examples that use the same `K`, `t`, `m`, `g`, or `l` as the
   generated task.
4. Preserve equation labels, section/page references, and 1-2 sentences of
   context.
5. Add an excerpt manifest:

```yaml
excerpt_id: wen-1995-kmatrix-formula
source: "Wen 1995, arXiv:cond-mat/9506066"
role: "method_formula"
allowed_for_tasks:
  - wen-kmatrix-laughlin-hidden-m
  - wen-kmatrix-2x2-hidden
contains_gold_answer: false
leakage_risk: low
notes: "Contains general formula only; generated K/t/l values differ per run."
```

### Positive Example

Good excerpt:

```text
In an Abelian FQH state described by an integer symmetric K matrix and charge
vector t, the filling fraction is computed as t^T K^{-1} t. Quasiparticles are
labeled by integer vectors l.
```

This teaches the method but does not reveal the answer for a generated `K`.

### Negative Example

Bad excerpt:

```text
For the Laughlin 1/3 state, K=3, the quasiparticle charge is 1/3 and the torus
ground-state degeneracy is 3.
```

This leaks the answer if the task uses `m=3`.

### Rule Of Thumb

The agent may see equations that map inputs to outputs. It should not see the
specific evaluated outputs for the same generated inputs.

## Task Family A: K-Matrix Hard Checks

### Prompt Shape

Give the agent:

- a short excerpt explaining the Abelian FQH K-matrix formalism;
- a hidden/generated `K` matrix and charge vector `t` in the visible prompt;
- required JSON output.

Example visible input:

```text
K = [[3, 1], [1, 3]]
t = [1, 1]
genus = 2
l_vectors = [[1,0], [0,1], [1,-1]]
```

### Hard-Check Fields

Verifier computes:

- `det_K = det(K)`
- `filling_fraction = t^T K^{-1} t`
- `torus_gsd = |det(K)|`
- `genus_gsd = |det(K)|^genus`
- `quasiparticle_charge(l) = t^T K^{-1} l`
- `exchange_statistics_theta_over_pi(l) = l^T K^{-1} l`
- `mutual_statistics_over_2pi(l1,l2) = l1^T K^{-1} l2`
- `chiral_central_charge_signature = signature(K)`

### Why It Is Search-Resistant

The formulas are public, but the concrete matrices and vectors are generated
per run. Search can recover the method but not the answer.

## Task Family B: Edge-Mode Consistency

### Prompt Shape

Give:

- an excerpt connecting bulk K-matrix data to edge chiral bosons;
- a generated `K` matrix with known signature.

Require structured output:

```json
{
  "num_edge_fields": 2,
  "num_right_movers": 2,
  "num_left_movers": 0,
  "net_chirality": 2,
  "edge_bulk_consistent": true
}
```

### Hard Checks

The verifier diagonalizes or computes the signature of `K` and checks:

- number of modes = matrix rank;
- right/left movers from signs of eigenvalues;
- net chirality = signature;
- consistency with the supplied edge claim.

## Task Family C: Source-Grounded Claim Extraction

### Prompt Shape

Give a page/excerpt packet from Wen's paper and ask for claims with source spans:

```json
{
  "claims": [
    {
      "claim_type": "bulk_edge_relation",
      "claim": "...",
      "source_span": "p. X, paragraph Y",
      "supports_topological_order": true
    }
  ]
}
```

### Hard Checks

This is less mathematically hard, but can still be constrained:

- source span must exist in the packet;
- claim type must be from a controlled enum;
- required keywords / equation identifiers must appear near the cited span;
- unsupported claims fail.

Use this as a secondary reading task, not the main hard-score task.

## Task Family D: Hidden-Convention Transform

### Prompt Shape

Give a K-matrix task and apply a generated unimodular basis change:

```text
K' = W^T K W
t' = W^T t
```

Ask the agent to identify invariant quantities.

### Hard Checks

Verifier checks:

- `det(K') = det(K)` up to sign;
- filling fraction invariant;
- ground-state degeneracy invariant;
- quasiparticle statistics transform consistently.

### Why This Tests Understanding

It prevents pure table lookup. The agent must know which objects are basis
dependent and which are invariant.

## Minimal v0.1 Task Set

Start with 5 tasks:

1. `wen-kmatrix-laughlin-hidden-m`
   - Visible: odd integer `m`.
   - Check: filling `1/m`, GSD on genus `g`, quasiparticle charge/statistics.

2. `wen-kmatrix-2x2-hidden`
   - Visible: generated positive-definite 2x2 integer K and t.
   - Check: determinant, filling, anyon charges/statistics.

3. `wen-edge-signature`
   - Visible: generated K.
   - Check: edge mode count and chirality.

4. `wen-basis-transform-invariance`
   - Visible: K, t, W.
   - Check: invariant quantities before/after transform.

5. `wen-source-span-bulk-edge`
   - Visible: controlled excerpt packet.
   - Check: source-span and enum-based claim extraction.

## Scoring

Primary score:

```text
hard_score = passed_checks / total_checks
```

Use diagnostic rubric only for:

- wrong formula selection;
- linear algebra error;
- source-grounding failure;
- bulk/edge confusion;
- convention confusion;
- unsupported extrapolation.

## Anti-Leakage

Do not expose:

- gold answers;
- hidden seed;
- verifier implementation;
- previous Kimi outputs.

The source paper itself can be visible, but task parameters must be generated
per run. This makes search useful only for background method, not for answers.

## First Implementation Target

Implement `wen-kmatrix-laughlin-hidden-m` first because it is simple:

Input:

```json
{
  "m": 5,
  "genus": 3,
  "l": 1
}
```

Expected verifier outputs:

```json
{
  "filling_fraction": "1/5",
  "torus_gsd": 5,
  "genus_gsd": 125,
  "quasiparticle_charge": "1/5",
  "exchange_statistics_theta_over_pi": "1/5"
}
```

Then scale to 2x2 K matrices once the runner/verifier pattern is stable.
