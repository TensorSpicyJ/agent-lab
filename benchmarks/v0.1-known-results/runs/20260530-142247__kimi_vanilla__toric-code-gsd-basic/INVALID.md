# Invalid Baseline Run

This run is not the official vanilla baseline.

Reason:

- The wrapper used `D:/Playground` as `cwd` instead of
  `D:/Playground/agent-lab`.
- Although the run produced an answer, the execution environment was not the
  intended benchmark root.

Interpretation:

Do not compare modified agents against this run.
