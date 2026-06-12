# Existing Physics Benchmarks Catalog v0.1

This directory classifies off-the-shelf physics-relevant benchmarks for local agent evaluation. It separates what can be used directly now from what needs licensing, access, multimodal handling, or custom front-end extraction.

Primary goal:
- keep benchmark provenance clear
- avoid mixing original benchmark questions with self-authored variants
- expose physics-domain coverage gaps before adding custom frontier tasks

Files:
- `catalog.md`: benchmark-by-benchmark classification
- `coverage-matrix.md`: physics field coverage
- `recommended-v0.1-suite.md`: practical first version to run locally
- `source-notes.md`: source links, constraints, and use boundaries
- `open-source-candidate-scan-2026-06-03.md`: expanded public/open-data physics benchmark scan
- `kimi26-open-physics-scorecard-2026-06-03.md`: aggregate local Kimi 2.6 scorecard across materialized open/public physics lanes
- `inclusion-status.yaml`: machine-readable included/registered status
- `physlib-local-scan-2026-06-02.md`: local repository file-count scan for PhysLib
- task-level attributes now live inside each included benchmark under `problem-metadata.yaml`
- `problem-attribute-schema.md`: field definitions for per-problem metadata
- `included-problem-index.json`: flattened index of all included problems
- `benchmark-source-profiles.yaml`: source-level benchmark attribute profiles
- `physlib-formal-shortlist-v0.1.yaml`: curated first-pass shortlist for a Lean formal lane
- local seed lane: [existing-physlib-formal-lane-v0.1](D:/Playground/agent-lab/benchmarks/existing-physlib-formal-lane-v0.1/README.md)
- diverse open-data lane: [existing-open-physics-diverse-v0.1](D:/Playground/agent-lab/benchmarks/existing-open-physics-diverse-v0.1/README.md)
- hard CMT stress lane: [existing-cmt-hard-stress-v0.1](D:/Playground/agent-lab/benchmarks/existing-cmt-hard-stress-v0.1/README.md)
