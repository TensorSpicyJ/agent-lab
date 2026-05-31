# Task: Wen K-Matrix Laughlin Hidden-m

This is a hard-scored benchmark task based on Wen-style Abelian FQH K-matrix
formalism.

Agent-visible files:

- `prompt.md`
- `source_packet/wen_kmatrix_excerpt.md`

Verifier-only files:

- `private/params.hidden.json`
- `verify.py`
- `answer_schema.json`

The current demo instance uses `K = [[7]]`, `t = [1]`, `genus = 2`, and
`l_vectors = [[1], [2]]`. In a real benchmark run, these parameters should be
generated per run and not mounted into the agent workspace.
