import json
import re
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
PARAMS_PATH = TASK_DIR / "private" / "params.hidden.json"
REPO_ROOT = TASK_DIR.parents[3]
FRAMEWORK_SCHEMA = REPO_ROOT / "design" / "physics-derivation-framework" / "schemas" / "derivation-record.schema.json"
LEDGER_SCHEMA = REPO_ROOT / "design" / "physics-derivation-framework" / "schemas" / "assumption-ledger.schema.json"


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise ValueError(f"Could not decode {path}")


def extract_json(text: str) -> dict:
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return json.loads(matches[-1])
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in answer")
    return json.loads(text[start : end + 1])


def norm(s) -> str:
    return re.sub(r"\s+", "", str(s or "").lower())


def contains_any(value, needles) -> bool:
    hay = norm(value)
    return any(norm(needle) in hay for needle in needles)


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def try_jsonschema_validate(answer: dict, ledger: list):
    try:
        import jsonschema
    except Exception as exc:
        return [
            {
                "name": "jsonschema_available",
                "passed": False,
                "detail": f"jsonschema unavailable: {exc}",
            }
        ]

    checks = []
    for name, schema_path, instance in [
        ("derivation_record_schema", FRAMEWORK_SCHEMA, answer),
        ("assumption_ledger_schema", LEDGER_SCHEMA, ledger),
    ]:
        try:
            jsonschema.validate(instance, load_json(schema_path))
            checks.append({"name": name, "passed": True, "detail": ""})
        except Exception as exc:
            checks.append({"name": name, "passed": False, "detail": str(exc).splitlines()[0]})
    return checks


def find_ledger_entry(ledger, expected_status, claim_needles):
    for entry in ledger:
        if not isinstance(entry, dict):
            continue
        if entry.get("status") != expected_status:
            continue
        claim = entry.get("claim", "")
        valid_when = entry.get("scope", {}).get("valid_when", "")
        invalid_when = entry.get("scope", {}).get("invalid_when", "")
        combined = f"{claim} {valid_when} {invalid_when}"
        if contains_any(combined, claim_needles):
            return entry
    return None


def dependency_references_valid(answer: dict) -> bool:
    step_ids = {s.get("id") for s in answer.get("derivation_trace", []) if isinstance(s, dict)}
    premise_ids = {p.get("id") for p in answer.get("physical_premises", []) if isinstance(p, dict)}
    translation_ids = {t.get("id") for t in answer.get("formal_translations", []) if isinstance(t, dict)}
    assumption_ids = {a.get("id") for a in answer.get("assumption_ledger", []) if isinstance(a, dict)}
    allowed = step_ids | premise_ids | translation_ids | assumption_ids
    for step in answer.get("derivation_trace", []):
        if not isinstance(step, dict):
            return False
        for dep in step.get("depends_on", []):
            if dep not in allowed and not str(dep).startswith("source:") and dep != "prompt":
                return False
    return True


def no_rejected_assumption_used_as_derivation_premise(answer: dict) -> bool:
    rejected = {a.get("id") for a in answer.get("assumption_ledger", []) if isinstance(a, dict) and a.get("status") == "rejected"}
    for step in answer.get("derivation_trace", []):
        rule = step.get("rule")
        deps = set(step.get("depends_on", []))
        if rule not in {"assumption_gate", "refusal_without_regime"} and deps & rejected:
            return False
    return True


def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    params = load_json(PARAMS_PATH)
    answer = extract_json(read_text_flexible(Path(sys.argv[1])))
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    ledger = answer.get("assumption_ledger", [])
    final = answer.get("final_answer", {})
    trace = answer.get("derivation_trace", [])
    verifications = answer.get("verification_checks", [])

    checks.extend(try_jsonschema_validate(answer, ledger))

    check("task_id", answer.get("task_id") == params["task_id"])
    check("source_excerpt_referenced", "tight-binding-effective-mass-minimal" in json.dumps(answer, ensure_ascii=False))

    check("global_effective_mass_not_determined", final.get("global_effective_mass_determined") is False)
    check("global_parabolic_rejected", final.get("global_parabolic_approximation_status") == "rejected")
    check("unconditional_effective_mass_null", final.get("unconditional_effective_mass") is None)
    check("requires_more_information", final.get("requires_more_information") is True)

    check("low_k_branch_conditional", final.get("low_k_branch_status") == "conditional")
    check("low_k_condition_present", contains_any(final.get("low_k_condition"), ["|ka|<<1", "|k*a|<<1", "small", "low-k"]))
    check("conditional_expansion_point", norm(final.get("conditional_expansion_point")) in {"k0=0", "k_0=0"})

    expected = params["expected_conditional_result"]
    check("conditional_effective_mass", contains_any(final.get("conditional_effective_mass"), ["hbar^2/(2*t*a^2)", "ℏ^2/(2*t*a^2)", "hbar^2/2ta^2"]))
    check("conditional_quadratic_energy", contains_any(final.get("conditional_quadratic_energy"), ["e0-2*t+t*a^2*k^2", "e0-2t+t(ka)^2", expected["quadratic_energy"]]))
    check("conditional_error_order", contains_any(final.get("conditional_error_order"), ["o((k*a)^4)", "o((ka)^4)", "fourth"]))

    rejected_global = find_ledger_entry(
        ledger,
        "rejected",
        ["global", "brillouin", "not a global approximation", "without regime"],
    )
    conditional_low_k = find_ledger_entry(
        ledger,
        "conditional",
        ["|ka|", "low-k", "k0=0", "small"],
    )
    check("ledger_rejects_global_approximation", rejected_global is not None)
    check("ledger_has_conditional_low_k_branch", conditional_low_k is not None)

    rules = [s.get("rule") for s in trace if isinstance(s, dict)]
    allowed = set(params["allowed_rules"])
    required = set(params["required_rules"])
    check("derivation_trace_minimum_steps", isinstance(trace, list) and len(trace) >= 3)
    check("rules_allowed", all(r in allowed for r in rules), f"rules={rules}")
    check("required_rules_present", required.issubset(set(rules)), f"missing={sorted(required - set(rules))}")
    check("dependency_references_valid", dependency_references_valid(answer))
    check("rejected_assumption_not_used_as_premise", no_rejected_assumption_used_as_derivation_premise(answer))

    check("verification_has_assumption_gate_pass", any(v.get("check_type") == "assumption_gate" and v.get("status") == "pass" for v in verifications if isinstance(v, dict)))

    raw = json.dumps(answer, ensure_ascii=False).lower()
    forbidden_unconditional = [
        "therefore the effective mass is",
        "the effective mass is hbar",
        "unconditionally",
        "global effective mass is",
    ]
    check("no_unconditional_effective_mass_claim", not any(phrase in raw for phrase in forbidden_unconditional))

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    print(json.dumps({
        "task_id": params["task_id"],
        "hard_score": round(passed / total, 4),
        "passed": passed,
        "total": total,
        "checks": checks,
    }, indent=2, ensure_ascii=False))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
