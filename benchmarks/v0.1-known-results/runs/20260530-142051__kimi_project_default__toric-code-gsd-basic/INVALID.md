# Invalid Baseline Run

This run is not a capability score.

Reason:

- The first wrapper version treated Kimi stderr output as a PowerShell exception.
- The run stopped before metadata and output were fully normalized.

Interpretation:

This was a wrapper bug, not an agent failure.
