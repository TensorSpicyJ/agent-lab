import json
import re
import sys
from pathlib import Path


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def extract_json(text: str):
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return json.loads(matches[-1])
    return json.loads(text[text.find("{") : text.rfind("}") + 1])


def norm(x):
    return re.sub(r"\s+", "", str(x or "").lower())


def has(x, needles):
    y = norm(x)
    return any(norm(n) in y for n in needles)


def main():
    if len(sys.argv) != 2:
        print("usage: python verify_short.py <answer.md>")
        return 2
    answer = extract_json(read_text(Path(sys.argv[1])))
    final = answer.get("final_answer", {})
    ledger = answer.get("assumption_ledger", [])
    steps = answer.get("steps", [])
    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    try:
        import jsonschema
        repo_root = Path(__file__).resolve().parents[4]
        schema_path = repo_root / "design" / "physics-derivation-framework" / "schemas" / "answer-card.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        jsonschema.validate(answer, schema)
        check("answer_card_schema", True)
    except Exception as exc:
        check("answer_card_schema", False, str(exc).splitlines()[0])

    check("task_id", answer.get("task_id") == "band-effective-mass-assumption-gate")
    check("global_not_determined", final.get("global_effective_mass_determined") is False)
    check("global_rejected", final.get("global_parabolic_approximation_status") == "rejected")
    check("unconditional_mass_null", final.get("unconditional_effective_mass") is None)
    check("low_k_conditional", final.get("low_k_branch_status") == "conditional")
    check("requires_more_information", final.get("requires_more_information") is True)
    check("condition_has_small_ka", has(final.get("low_k_condition"), ["|ka|<<1", "|k*a|<<1"]))
    check("expansion_point_k0", norm(final.get("conditional_expansion_point")) in {"k0=0", "k_0=0"})
    check("mass_formula", has(final.get("conditional_effective_mass"), ["hbar^2/(2*t*a^2)", "hbar^2/2ta^2"]))
    check("energy_formula", has(final.get("conditional_quadratic_energy"), ["e0-2*t+t*a^2*k^2", "e0-2t+t*a^2*k^2"]))
    check("error_order", has(final.get("conditional_error_order"), ["o((k*a)^4)", "o((ka)^4)"]))
    check("ledger_rejected", any(a.get("status") == "rejected" and has(a.get("claim"), ["global", "parabolic"]) for a in ledger if isinstance(a, dict)))
    check("ledger_conditional", any(a.get("status") == "conditional" and has(a.get("claim") + a.get("valid_when", ""), ["low-k", "|ka|", "k0=0"]) for a in ledger if isinstance(a, dict)))
    rules = [s.get("rule") for s in steps if isinstance(s, dict)]
    check("required_rules", {"refusal_without_regime", "conditional_branch", "curvature_effective_mass"}.issubset(set(rules)), f"rules={rules}")

    passed = sum(c["passed"] for c in checks)
    print(json.dumps({
        "task_id": "band-effective-mass-assumption-gate",
        "hard_score": round(passed / len(checks), 4),
        "passed": passed,
        "total": len(checks),
        "checks": checks,
    }, ensure_ascii=False, indent=2))
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())
