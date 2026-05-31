# Invalid Baseline Run

This run is not a capability score.

Reason:

- Agent: `kimi_vanilla`
- Command requested an explicit empty `--skills-dir`.
- Kimi Code exited with `-1073740791` before producing output.
- `stdout` and `stderr` were empty.

Interpretation:

The current `kimi --skills-dir <empty>` isolation path is not a usable vanilla
baseline on this machine. Treat this as a Kimi CLI/environment issue until
reproduced or resolved.

Next action:

Use `kimi_project_default` as the practical baseline for now, and later retry a
true vanilla baseline with another isolation method or Kimi Code version.
