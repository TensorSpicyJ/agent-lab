# Anti-Leakage and Anti-Search Policy

Date: 2026-05-30

## Core Rule

Do not trust the agent not to search. Design the benchmark so that:

1. search is technically blocked or fully logged;
2. public search cannot directly reveal the answer;
3. the verifier checks task-specific hidden variants;
4. any network/tool use violation invalidates the run.

## Threat Model

An agent may obtain answers through:

- web search;
- local file search outside the benchmark packet;
- cached prior conversations or memory;
- model pretraining memorization;
- prompt leakage from gold files or verifier code;
- tool logs, previous runs, or accidentally visible outputs.

## Required Controls

### 1. Environment Isolation

Run benchmark attempts in a sandbox where:

- network access is disabled by default;
- web/search tools are unavailable;
- workspace contains only the task input packet, runner, and allowed libraries;
- gold files and verifier internals are not visible to the agent;
- previous run outputs are not mounted into the agent workspace.

If network cannot be disabled, every network-capable tool call must be logged,
and any call not explicitly allowed makes the run invalid.

### 2. Private Variants

For public known-result tasks, do not ask only for the public theorem. Generate
private variants whose answer is mechanically derived from hidden parameters.

Examples:

- change topology: genus `g`, boundary type, number of punctures;
- change lattice size or graph counts while preserving Euler constraints;
- ask for several special cases in one task;
- use synthetic Hamiltonian parameters with a known closed-form output;
- perturb a paper derivation with a small controlled convention change.

The verifier should compute the expected answer from hidden task parameters
rather than store only a static public answer.

### 3. Split Public Prompt and Hidden Gold

The agent sees:

- problem statement;
- allowed source packet;
- required output schema.

The agent must not see:

- gold answer;
- verifier implementation;
- hidden parameter seed;
- previous scored outputs.

### 4. Structured Answer

Require machine-gradable fields:

- final answer;
- required intermediate equations;
- assumptions as enums or booleans;
- known limits;
- source spans if sources are provided;
- forbidden claims.

Free-form derivation text is allowed, but it is not the primary grade.

### 5. Audit Trail

Each run must record:

- command line;
- working directory;
- network status;
- available tools;
- mounted files;
- prompt checksum;
- output checksum;
- verifier checksum;
- tool-call log if available.

Runs missing this metadata are diagnostic only, not benchmark evidence.

## Applying This To `toric-code-gsd-basic`

The current toric-code task is useful as a hard-scored smoke test, but it is not
search-resistant because `GSD = 4` is public and memorized.

To make it search-resistant, replace it with hidden variants such as:

```text
Given a closed orientable surface with hidden genus g, compute:
  encoded_qubits = 2g
  GSD = 4^g

Given a cellulation with hidden V, E, F satisfying Euler characteristic,
compute:
  independent_stabilizers = V + F - 2
  encoded_qubits = E - (V + F - 2)
```

The verifier should compute these from a hidden `params.json`, and the agent
should only see the public problem statement plus visible parameter values.

## Run Validity

A run is invalid if:

- network/search is used when forbidden;
- gold files are visible to the agent;
- verifier code is visible before answer generation;
- previous outputs are visible;
- task prompt checksum does not match manifest;
- output is manually edited before verification.
