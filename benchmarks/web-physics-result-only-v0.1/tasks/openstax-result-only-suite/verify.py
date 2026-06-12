import json
import math
import re
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
GOLD_PATH = TASK_DIR / "private" / "gold.json"


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def extract_json(text: str) -> dict:
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return json.loads(matches[-1])
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in answer")
    return json.loads(text[start : end + 1])


def normalize_scientific_text(text: str) -> str:
    normalized = str(text)
    normalized = normalized.replace("×", "x").replace("·", "*")
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(
        r"([+-]?\d+(?:\.\d+)?)\s*(?:x|\*)\s*10\s*\^?\s*([+-]?\d+)",
        lambda m: f"{m.group(1)}e{m.group(2)}",
        normalized,
        flags=re.IGNORECASE,
    )
    return normalized


def unit_factor(text: str, expected_unit: str) -> float:
    lower = text.lower()
    if expected_unit == "J":
        if re.search(r"\bkj\b|kilojoule", lower):
            return 1.0e3
        if re.search(r"\bmj\b|megajoule", lower):
            return 1.0e6
    if expected_unit == "kg":
        if re.search(r"\bg\b|gram", lower) and not re.search(r"\bkg\b|kilogram", lower):
            return 1.0e-3
    if expected_unit == "ohm":
        if "kΩ" in text or re.search(r"\bko?hm\b|kiloohm", lower):
            return 1.0e3
    return 1.0


def parse_quantity(value, expected_unit: str):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        text = normalize_scientific_text(value)
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", text)
        if not match:
            return None
        return float(match.group(0)) * unit_factor(text, expected_unit)
    return None


def is_close(actual: float, expected: float, rel_tol: float, abs_tol: float) -> bool:
    return math.isclose(actual, expected, rel_tol=rel_tol, abs_tol=abs_tol)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    try:
        answer = extract_json(read_text_flexible(Path(sys.argv[1])))
    except Exception as exc:
        print(json.dumps({
            "task_id": "openstax-result-only-suite",
            "hard_score": 0.0,
            "passed": 0,
            "total": len(gold["answers"]),
            "error": f"json_parse_failed: {exc}",
            "checks": [],
        }, ensure_ascii=False, indent=2))
        return 1

    answers = answer.get("answers", answer)
    checks = []

    def add_check(field: str, passed: bool, detail: dict):
        checks.append({
            "field": field,
            "passed": bool(passed),
            **detail,
        })

    for field, spec in gold["answers"].items():
        expected = float(spec["value"])
        raw_actual = answers.get(field)
        actual = parse_quantity(raw_actual, spec.get("unit", "dimensionless"))
        if actual is None:
            add_check(field, False, {
                "expected": expected,
                "actual_raw": raw_actual,
                "actual_parsed": None,
                "reason": "missing_or_unparseable",
            })
            continue

        compare_actual = abs(actual) if spec.get("allow_abs_value") else actual
        abs_error = abs(compare_actual - expected)
        rel_error = abs_error / abs(expected) if expected != 0 else abs_error
        passed = is_close(compare_actual, expected, float(spec["rel_tol"]), float(spec["abs_tol"]))
        add_check(field, passed, {
            "expected": expected,
            "actual_raw": raw_actual,
            "actual_parsed": actual,
            "compared_value": compare_actual,
            "abs_error": abs_error,
            "rel_error": rel_error,
            "rel_tol": spec["rel_tol"],
            "abs_tol": spec["abs_tol"],
        })

    passed = sum(1 for check in checks if check["passed"])
    total = len(checks)
    result = {
        "benchmark_id": gold["benchmark_id"],
        "task_id": gold["task_id"],
        "hard_score": round(passed / total, 4) if total else 0.0,
        "passed": passed,
        "total": total,
        "checks": checks,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
