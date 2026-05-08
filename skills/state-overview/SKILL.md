---
name: state-overview
description: Load the current research state for a research line and present a structured overview. Use at the start of any research session, when switching lines, or when the user asks "what's the state of X?".
---

# State Overview

Load and present the current state of a research line from the research knowledge layer. This is the agent's "boot-up" — it must be done before any research reasoning.

## Context Budget

**MUST load:**
- `research-knowledge/INDEX.md`
- `research-knowledge/lines/<line>/STATE.md` (full)
- `research-knowledge/lines/<line>/hypotheses.md` — one-liner summary per hypothesis only (not full evidence chains)
- `research-knowledge/lines/<line>/open-questions.md` — high-priority questions only

**MUST NOT load:**
- Individual paper insight files (load on demand if a specific paper is referenced)
- Full derivation or experiment records
- methodology files
- Other research lines' STATE files (unless cross-line task)

**Rule**: The overview should fit in one screen. Don't deep-dive into evidence details — that's for the specific skill that needs them.

## When to Use

- At the start of any research session (read CLAUDE.md §0 first)
- When switching between research lines
- When the user asks "现在什么状态", "progress", "overview"
- Before proposing new hypotheses or experiments

## Workflow

### 1. Read INDEX first

Always start from `research-knowledge/INDEX.md` to understand the global research landscape.

### 2. Load the target line

Read in order:
1. `research-knowledge/lines/<line>/STATE.md` — current facts, hypotheses summary, next actions
2. `research-knowledge/lines/<line>/hypotheses.md` — detailed hypothesis tracking with evidence
3. `research-knowledge/lines/<line>/open-questions.md` — prioritized open questions

### 3. Check cross-line connections

If the line has cross-line links (check STATE.md frontmatter and `cross-cutting/connections.md`), note them — they may be relevant to the current task.

### 4. Present structured overview

Output a concise summary covering:

```
## <line-name> — 当前状态

### 已确立
- <3-5 key established facts with sources>

### 活跃假说 (N)
- H1: <one-liner> [evidence_type: theoretical|experimental|mixed] [状态: active|stalled|validated]

### 最优先的开放问题
- Q1: <one-liner> (阻塞因素: <what's blocking>)

### 下一步建议
- <ranked next actions>
```

### 5. Act on the overview

After presenting, don't wait — if the research context makes the next action obvious, propose it directly:
- "最自然的下一步是 X，要继续吗？"
- If there's new data or a paper to process, suggest running `paper-to-insight` or `experiment-analyzer`

## Key Rules

- Always present state before reasoning — don't make research suggestions without first loading STATE.md
- If STATE.md hasn't been updated in a while, note this but don't block on it
- The overview should fit in one screen — prioritize, don't dump everything
- Don't re-read files you just read in the same session — use what's in context
