# PhysLib Formal Smoke Mini 3

Fill only the Lean proof bodies after `by`.

Output exactly one JSON object with these keys:

- `informal_definition_deps`
- `informal_lemma_tag`
- `todo_info_line`

Each value must be a Lean proof body string. Do not include explanations.

## Problem 1

```lean
import Physlib.Meta.Informal.Basic

example (deps : List Lean.Name) (tag : String) :
    (⟨deps, tag⟩ : InformalDefinition).deps = deps := by
  -- fill proof body
```

## Problem 2

```lean
import Physlib.Meta.Informal.Basic

example (deps : List Lean.Name) (tag : String) :
    (⟨deps, tag⟩ : InformalLemma).tag = tag := by
  -- fill proof body
```

## Problem 3

```lean
import Physlib.Meta.TODO.Basic

open Physlib

example (content tag : String) (fileName : Lean.Name) (line : Nat) :
    ({ content := content, fileName := fileName, line := line, tag := tag } : todoInfo).line = line := by
  -- fill proof body
```
