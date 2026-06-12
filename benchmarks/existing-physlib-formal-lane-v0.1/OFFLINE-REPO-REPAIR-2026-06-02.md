# Offline Repo Repair 2026-06-02

Temporary clone:
- `C:/Users/TaiS/AppData/Local/Temp/physlean-inspect`

Why this note exists:
- the formal benchmark verifier relies on a local PhysLib clone
- the key environment fixes in this session were applied to that temporary clone, not to a checked-in workspace repo
- this note records the exact repair state so later runs do not have to rediscover it

Repairs applied:
- disabled `doc-gen4` in the temporary clone `lakefile.lean` because theorem checking does not need documentation-generation dependencies
- cleaned `lake-manifest.json` to remove `doc-gen4`-only dependencies:
  - `doc-gen4`
  - `leansqlite`
  - `UnicodeBasic`
  - `BibtexQuery`
  - `MD4Lean`
- corrected the `Cli` package remote to `https://github.com/leanprover/lean4-cli`
- replaced the broken local `Cli` checkout with a matching cached checkout at revision `7802da01beb530bf051ab657443f9cd9bc3e1a29`
- rewrote `lake-manifest.json` as UTF-8 without BOM so `lake` can parse it

Verifier-side fixes:
- the formal verifier now prepends the PhysLib repo root to `LEAN_PATH`
- `object file ... does not exist` is classified as `module_prebuild_required`

Current observed state after repair:
- `lake env lean BenchSmoke.lean` now reaches Lean module loading instead of failing on `git` dependency fetch
- sample verification for `visviva-speedcircular-sq-proof` returns:
  - `status = environment_error`
  - `error = module_prebuild_required`
- partial local build evidence after the interrupted prebuild attempt:
  - `mathlib` built objects observed: `721`
  - `Physlib` built objects observed: `2`

Open blocker:
- there is no other local `Lean 4.29.1` `mathlib` build cache on this machine to reuse
- targeted `lake build` now starts correctly, but real theorem checking still needs the required PhysLib modules to finish prebuilding
