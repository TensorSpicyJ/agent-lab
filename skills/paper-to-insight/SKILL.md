---
name: paper-to-insight
description: Extract structured insights from a research paper and write them into the research knowledge layer. Use when the user provides a paper (PDF, DOI, arXiv link, or title) and wants it archived as reusable knowledge.
---

# Paper → Insight

Read a research paper and extract structured insights into the research knowledge layer (`D:\Playground\research-knowledge\`). Every claim must be source-grounded.

## Context Budget

**MUST load:**
- The target paper (PDF/abstract)
- `research-knowledge/INDEX.md` (to identify target line)
- `research-knowledge/lines/<line>/STATE.md` — hypotheses summary section only
- `research-knowledge/lines/<line>/hypotheses.md` — only hypotheses relevant to the paper's topic

**MUST NOT load:**
- Full experiment data files
- Other papers in the line's `papers/` directory (unless cross-referencing)
- methodology files (unless the paper is methods-focused)
- Other research lines' STATE files

**Rule**: If context exceeds ~500 lines of input, stop loading and proceed with what's loaded.

## When to Use

- User gives you a paper PDF, DOI, arXiv link, or title+author
- User says "读这篇", "归档这篇", "提取这篇"
- After a literature search session when papers need to be archived
- When you encounter a paper during research and want to preserve the key findings

## Workflow

### 1. Identify the research line

Ask or determine which research line(s) the paper belongs to:
- `lsco-single-layer`
- `superconducting-diode`
- `sc-magnetic`
- `topological-order`

A paper can cross lines — note `cross-line` in the frontmatter.

### 2. Read the paper

- If given a PDF path, read it directly
- If given a DOI or arXiv ID, search for it and fetch the abstract + key content
- If the paper cannot be accessed, note this and extract what you can from the metadata

### 3. Load current state

Read the target line's current files before writing:
1. `research-knowledge/lines/<line>/STATE.md`
2. `research-knowledge/lines/<line>/hypotheses.md`
3. `research-knowledge/lines/<line>/open-questions.md`

This ensures you know what's already established and can connect the new paper to existing knowledge.

### 4. Extract structured insight

Write to `research-knowledge/lines/<line>/papers/<slug>.md` using this template:

```markdown
---
type: paper-insight
status: extracted
line: <primary-line>
confidence: high | medium | low
cross-line: [<other-lines>]  # optional
source_grounding:
  doi: <DOI>
  venue: <Journal Volume, Page (Year)>
  authors: <First Author et al.>
  key_figure: <most important figure>
  key_equation: <most important equation>  # optional
  arxiv: <arXiv link>  # if applicable
  publication_status: published | preprint
---

# <Title>

## 一句话结论
- <1 sentence that captures the core finding — this is what the agent reads first>

## 关键发现
- <Finding 1>
- <Finding 2>
- <Finding 3>

## 与我们的关系
- **涉及线**: <line>
- **支撑/挑战假说**: <which hypothesis does this affect?>
- **适用边界**: <what conditions/limits apply?>

## 可行动的下一步
- <concrete action this paper enables>

## 方法标签
- <method 1>
- <method 2>
```

### 5. Update knowledge state

After writing the paper insight, update the line's knowledge files:

**Update STATE.md:**
- Add new established facts (only if confidence is high and from published work)
- Add to "最近更新"
- Update "下一步" if the paper enables new actions

**Update hypotheses.md:**
- If the paper supports or challenges an existing hypothesis, add evidence
- If the paper suggests a new hypothesis, create it

**Update open-questions.md:**
- If the paper answers an existing open question, mark it resolved
- If the paper raises new questions, add them

**Update cross-cutting/connections.md:**
- If the paper connects multiple research lines, add the connection

### 6. Report to user

Summarize:
- What paper was processed
- Which line(s) it was written to
- Which hypotheses were affected
- Any new next actions discovered

## Source Grounding Rules

- Every factual claim must link to a source: DOI, specific figure, equation number, or experiment sample ID
- Distinguish established facts (confidence: high, from published work) from tentative findings (confidence: medium/low, from preprints or single studies)
- Preprints must be labeled `publication_status: preprint` and confidence capped at `medium`
- In-house experimental data are valid sources — cite sample ID (e.g., `#156 XRD`)
