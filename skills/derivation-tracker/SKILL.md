---
name: derivation-tracker
description: Track mathematical derivations and formal proofs, record proof steps, lemma dependencies, and open gaps. Use when doing theoretical work, reading theory papers, or when agent detects derivation chain gaps.
---

# Derivation Tracker

Record and track mathematical derivations, formal proofs, and theoretical arguments in the research knowledge layer. This is the theoretical counterpart to `experiment-analyzer`.

## Context Budget

**MUST load:**
- Target derivation source (paper PDF, theorem statement, or user's scratch work)
- `research-knowledge/lines/<line>/STATE.md` — established facts and active hypotheses only
- `research-knowledge/lines/<line>/hypotheses.md` — hypotheses with `evidence_type: theoretical` or `mixed`
- Existing `research-knowledge/lines/<line>/derivations/<topic>.md` (if any)
- `research-knowledge/methodology/theoretical/formalisms.md` — relevant formalism section only

**MUST NOT load:**
- Experiment data or `experiments/` files
- Full paper insight files (load only if directly referenced)
- Other lines' derivations (unless cross-line dependency explicitly noted)
- `cross-cutting/` (unless theory-experiment bridge is the task)

**Rule**: For formalized proofs (Lean 4/Coq), load the `.lean`/`.v` source file instead of the paper when possible.

## When to Use

- User is working through a derivation ("推一下这个", "证明这个")
- User gives a theory paper with heavy math
- Agent detects a derivation gap while reading STATE.md (hypothesis has `evidence_type: theoretical` but no linked derivation)
- Formal proof needs updating (new lemma, gap found, `sorry` removed)

## Workflow

### 1. Identify the derivation topic

Determine:
- Which research line? (`topological-order`, `superconducting-diode`, etc.)
- What is the target theorem/claim?
- Is this formalized (Lean/Coq) or hand-derived?
- Does it support an existing hypothesis? (check hypotheses.md)

### 2. Load existing state

Read:
1. `research-knowledge/lines/<line>/STATE.md` — know what's established
2. `research-knowledge/lines/<line>/hypotheses.md` — find which hypothesis this derivation serves
3. Existing derivations in `derivations/` — avoid duplication, find dependencies

### 3. Verify formalization (if applicable)

If the derivation has a Lean 4 formalization, run verification **before** writing the record:

```bash
# 1. Build status
cd <repo-path> && lake build
# → record exit code as build_status: pass | fail

# 2. Find gaps (sorry/admit/axiom)
grep -rn "sorry\|admit\|axiom" <repo-path>/<module-dir>/ --include="*.lean"
# → each hit becomes an open_gaps entry of type formalization_gap

# 3. Extract theorem list
grep -n "^theorem\|^lemma" <file>.lean
# → record as lemma_dependencies or theorems list
```

**Rules:**
- Only run these commands if `repo_path` is provided by user or detected
- If `lake build` fails, derivation status cannot be `complete`
- `sorry`/`admit` hits must be recorded as gaps even if user thinks they're "temporary"

### 4. Record the derivation

Write to `research-knowledge/lines/<line>/derivations/<topic>.md` using this template:

```markdown
---
type: derivation
line: <line>
status: in-progress | complete | stalled
confidence: high | medium | low
formalization:
  status: none | partial | complete
  tool: Lean 4 | Coq | Mathematica | none
  repo_path: <path to formalization>  # e.g., topological-order-lean/TopoOrder/ToricCode.lean
  last_verified: <date>
inputs:
  - <source 1: paper DOI or theorem name>
  - <source 2: previous derivation file>
outputs:
  - <theorem/lemma name>
  - <corollary>
open_gaps:
  - type: unproven_lemma
    description: <what needs to be proved>
    blocks: <which output is blocked>
  - type: approximation
    description: <what was approximated>
    justification: <why it's justified>
  - type: assumption
    description: <unverified assumption>
    impact: <what fails if assumption is wrong>
  - type: formalization_gap
    description: <what's not yet in Lean/Coq>
    target: <which .lean file>
lemma_dependencies:
  - lemma: <lemma name>
    status: proved | used-as-axiom | unproven
    source: <where it comes from>
    used_in: <which step uses it>
---

# <Topic>

## Goal
<1-2 sentences: what are we proving/deriving?>

## Key Steps

### Step 1: <name>
- **Input**: <what we start from>
- **Operation**: <what we do>
- **Output**: <intermediate result>
- **Source**: <paper equation number or previous lemma>

### Step 2: <name>
...

## Current Status
- <what's done>
- <what's blocked>

## Open Gaps Detail

### <Gap 1>
- **Type**: unproven_lemma / approximation / assumption / formalization_gap
- **Description**: 
- **Impact**: <what can't proceed without this>
- **Possible resolution**: <ideas for closing the gap>

## Connections
- **Supports hypothesis**: <H1, H2, etc.>
- **Depends on derivation**: <other derivation file>
- **Used by**: <what downstream work uses this>
```

### 5. Update knowledge state

**Update STATE.md:**
- If derivation reaches `status: complete`, note in "最近更新"
- If new established fact emerges, add to established section (but mark as "待 promotion" until human review)
- Update "下一步" with gap-closing actions

**Update hypotheses.md:**
- Link derivation to supporting hypothesis
- Update confidence based on derivation progress
- If formalization is complete, raise confidence

**For formalized proofs (Lean 4):**
- Verify `lake build` passes
- Check no `sorry`/`admit` in the proof path
- Record the theorem name and file path in the derivation frontmatter

### 6. Report to user

Summarize:
- What was recorded
- Current status (complete / in-progress / stalled)
- Open gaps and their impact
- Next steps to close gaps

## Special Handling for Formalized Proofs

When the derivation is a Lean 4 formalization:

1. **Load the `.lean` source** instead of paper when possible
2. **Record theorem map**: list all lemmas/theorems in dependency order
3. **Track `sorry`/`admit`**: each is an `open_gaps` entry of type `formalization_gap`
4. **Verify build**: note `lake build` status in frontmatter
5. **Link to checkpoint docs**: if the repo has `docs/TORIC-CODE-CHECKPOINT.md` style docs, reference them

Example formalization record:
```yaml
formalization:
  status: complete
  tool: Lean 4
  repo_path: topological-order-lean/TopoOrder/ToricCode/GroundSpaceEquivalence.lean
  last_verified: 2026-04-29
  build_status: pass
  theorems:
    - full_gsd_eq_four
    - groundSpaceLinearEquivSectorSpace
    - readoutPairEquivFin4
```

## Source Grounding Rules

- Every step must cite: paper equation number, theorem name, or previous lemma file
- Formalized proofs: cite `.lean` file and theorem name
- Approximations must be explicitly labeled with justification
- `used-as-axiom` lemmas must be flagged — they are hidden assumptions
