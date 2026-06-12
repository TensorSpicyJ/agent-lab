# Run Summary

- benchmark: `existing-scibench-physics-result-only-v0.1`
- task: `scibench-physics-mixed-8`
- agent: `kimi26_code_allowed`
- model alias: `kimi-code/kimi-for-coding`
- local display note: `Kimi-k2.6`
- result: `7/8`
- hard_score: `0.8750`
- no_code_requested: `false`
- agent_created_files: `[]`

Failure:
- `matter_17_1_hydrogenic_heplus_energy_ev`
  - expected: `-6.04697`
  - actual: `-6.04`

Notes:
- temp cwd initially contained only `prompt.md`
- gold, verifier, and run history were not mounted into temp cwd
- network was requested off in prompt, but not system-enforced
