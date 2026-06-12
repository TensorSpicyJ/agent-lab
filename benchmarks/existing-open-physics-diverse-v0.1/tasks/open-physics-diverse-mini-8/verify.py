import json
import math
import re
import sys
from pathlib import Path


TASK_ROOT = Path(__file__).resolve().parent
GOLD_PATH = TASK_ROOT / "private" / "gold.json"


def load_output(path: Path):
    raw = path.read_bytes()
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff") or b"\x00" in raw[:64]:
        text = raw.decode("utf-16", errors="replace").strip()
    else:
        text = raw.decode("utf-8", errors="replace").strip()
    text = text.lstrip("\ufeff").strip()
    if text.startswith("•"):
        text = text[1:].strip()
    def parse_jsonish(candidate: str):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # LLMs often emit LaTeX inside JSON strings as \hbar or \frac.
            # Those are invalid JSON escapes, so preserve them as literal backslashes.
            repaired = re.sub(r"\\(?![\"\\/bfnrtu])", r"\\\\", candidate)
            return json.loads(repaired)
    try:
        return parse_jsonish(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if not match:
            raise
        return parse_jsonish(match.group(0))


def parse_float(value):
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        match = re.search(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?", cleaned)
        if match:
            return float(match.group(0))
    raise ValueError(f"cannot parse numeric value from {value!r}")


def norm_symbol(value):
    text = str(value).strip()
    text = re.sub(r"\^\{([^{}]+)\}", r"^\1", text)
    text = re.sub(r"\\frac\{1\}\{2\}", "1/2*", text)
    text = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"(\1)/(\2)", text)
    replacements = {
        "\\hbar": "hbar",
        "\\omega": "omega",
        "\\frac": "frac",
        "ω": "omega",
        "ℏ": "hbar",
        " ": "",
        "\\,": "",
        "\\left": "",
        "\\right": "",
        "{": "",
        "}": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.lower()
    text = text.replace("frac", "")
    text = text.replace("*", "")
    text = text.replace("\\", "")
    text = text.replace("1/2hbaromega", "hbaromega/2")
    text = text.replace("−", "-")
    return text


def parse_choice_set(value):
    if isinstance(value, list):
        raw = ";".join(str(v) for v in value)
    else:
        raw = str(value)
    tokens = re.findall(r"\b[a-i]\b", raw.lower())
    if not tokens and ";" in raw:
        tokens = [part.strip().lower() for part in raw.split(";") if part.strip()]
    return sorted(set(tokens))


def grade(gold, actual):
    checks = []
    passed = 0
    for item in gold["checks"]:
        field = item["field"]
        result = {
            "field": field,
            "type": item["type"],
            "source": item.get("source"),
            "domain": item.get("domain"),
            "difficulty": item.get("difficulty"),
            "passed": False,
            "expected": item.get("expected"),
            "actual_raw": actual.get(field),
        }
        try:
            if item["type"] == "numeric":
                expected = float(item["expected"])
                parsed = parse_float(actual.get(field))
                abs_error = abs(parsed - expected)
                rel_error = abs_error / max(abs(expected), 1e-12)
                ok = abs_error <= item.get("abs_tol", 0.0) or rel_error <= item.get("rel_tol", 0.0)
                result.update(
                    {
                        "actual_parsed": parsed,
                        "abs_error": abs_error,
                        "rel_error": rel_error,
                        "rel_tol": item.get("rel_tol"),
                        "abs_tol": item.get("abs_tol"),
                        "passed": ok,
                    }
                )
            elif item["type"] == "symbolic":
                actual_norm = norm_symbol(actual.get(field))
                expected_norms = [norm_symbol(item["expected"])]
                expected_norms.extend(norm_symbol(x) for x in item.get("alternatives", []))
                ok = actual_norm in expected_norms
                result.update(
                    {
                        "actual_normalized": actual_norm,
                        "expected_normalized": sorted(set(expected_norms)),
                        "passed": ok,
                    }
                )
            elif item["type"] == "choice_set":
                actual_set = parse_choice_set(actual.get(field))
                expected_set = sorted(item["expected"])
                ok = actual_set == expected_set
                result.update(
                    {
                        "actual_parsed": actual_set,
                        "expected": expected_set,
                        "passed": ok,
                    }
                )
            else:
                result["error"] = f"unknown check type {item['type']!r}"
        except Exception as exc:
            result["error"] = str(exc)
        if result["passed"]:
            passed += 1
        checks.append(result)
    total = len(checks)
    return {
        "benchmark_id": gold["benchmark_id"],
        "task_id": gold["task_id"],
        "hard_score": passed / total if total else math.nan,
        "passed": passed,
        "total": total,
        "checks": checks,
    }


def main(argv):
    if len(argv) != 2:
        print("usage: verify.py OUTPUT_JSON_OR_MD", file=sys.stderr)
        return 2
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    actual = load_output(Path(argv[1]))
    score = grade(gold, actual)
    print(json.dumps(score, indent=2, ensure_ascii=False))
    return 0 if score["passed"] == score["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
