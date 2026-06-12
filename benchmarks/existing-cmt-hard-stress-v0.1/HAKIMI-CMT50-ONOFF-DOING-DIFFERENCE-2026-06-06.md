# Hakimi CMT50 ON/OFF Doing-Difference Audit

- Run: `20260606-003930__hakimi013_deepseek_watchdog__cmt_hard_research_50__full50_onoff_watchdog_20260606`
- Model: `deepseek/deepseek-v4-pro`
- Window: `2026-06-06T00:39:30.209392+08:00` to `2026-06-06T04:47:52.533835+08:00`

## Score

| Mode | Correct | Valid JSON | Timeout/no answer | Passed problems |
|---|---:|---:|---:|---|
| experimental_default_on | 5/50 | 44/50 | 6 | 06, 22, 26, 27, 49 |
| experimental_flags_off | 5/50 | 40/50 | 10 | 05, 06, 16, 27, 36 |

## Doing Difference

| Category | Count | Problems |
|---|---:|---|
| Both correct | 2 | 06, 27 |
| ON correct only | 3 | 22, 26, 49 |
| OFF correct only | 3 | 05, 16, 36 |
| Both wrong, same answer | 12 | 04, 08, 10, 20, 21, 29, 31, 32, 35, 41, 44, 46 |
| Both wrong, different answers | 19 | 01, 02, 07, 09, 11, 13, 14, 15, 18, 19, 28, 30, 34, 37, 38, 39, 40, 47, 50 |
| ON no answer, OFF wrong | 3 | 03, 24, 43 |
| OFF no answer, ON wrong | 5 | 12, 17, 25, 33, 42 |
| Both timeout/no answer | 3 | 23, 45, 48 |

## Error Attribution

| Mode | Failure reason | Count |
|---|---|---:|
| experimental_default_on | choice_over_selected | 7 |
| experimental_default_on | choice_under_selected | 5 |
| experimental_default_on | choice_wrong_set | 12 |
| experimental_default_on | numeric_value_mismatch | 3 |
| experimental_default_on | runtime_timeout_no_json | 6 |
| experimental_default_on | symbolic_format_or_extra_lhs | 1 |
| experimental_default_on | symbolic_formula_mismatch | 11 |
| experimental_flags_off | choice_over_selected | 5 |
| experimental_flags_off | choice_under_selected | 5 |
| experimental_flags_off | choice_wrong_set | 11 |
| experimental_flags_off | numeric_value_mismatch | 4 |
| experimental_flags_off | runtime_timeout_no_json | 10 |
| experimental_flags_off | symbolic_format_or_extra_lhs | 1 |
| experimental_flags_off | symbolic_formula_mismatch | 9 |

## Success Review

| Mode | Problem | Review | Note |
|---|---:|---|---|
| experimental_flags_off | 05 | uncertain_capability | Reasoned about TBG symmetries, but the tool trace says the prompt line looked truncated. |
| experimental_default_on | 06 | capability | Commutation reasoning for N, S^z, and eta^2; no gold-file evidence. |
| experimental_flags_off | 06 | capability | Same stable commutation result as ON. |
| experimental_flags_off | 16 | capability_low_confidence | Long Hubbard-ring reasoning with explicit uncertainty; final a;d matched verifier. |
| experimental_default_on | 22 | format_sensitive | Answered N_k B. OFF answered f = N_k B, which is physically equivalent but fails the strict expected form. |
| experimental_default_on | 26 | capability | Magnetic-translation/gauge-invariance reasoning led to b;c;e; OFF timed out. |
| experimental_default_on | 27 | capability_with_parameter_cue | Derived O_n = E_n - E_{n-1}; listed parameters strongly constrain the form. |
| experimental_flags_off | 27 | capability_with_parameter_cue | Same derivation as ON; parameters strongly constrain the form. |
| experimental_flags_off | 36 | capability | Kitaev/PEPS operator mapping reasoning led to a;b. |
| experimental_default_on | 49 | capability | Long SU(2) and C4 representation-counting trace; OFF timed out. |

## Audit Notes

- No gold/private/sample-correct file leakage was found in the log scan.
- Several prompts expose a `Parameters` list; that can cue output variables or answer format, especially for choice-set items.
- Problem 22 is a verifier-format sensitivity case: OFF gave `f = N_k B`, while the verifier expected only `N_k B`.
- The total score is tied, but ON produced more valid answers and fewer timeouts.
