import json
import math
import re
import sys
import textwrap
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


def extract_code(text: str) -> str:
    lines = text.splitlines()
    start = None
    end = None
    for index, line in enumerate(lines):
        if line.lstrip(" \t\u2022").startswith("```"):
            start = index + 1
            break
    if start is not None:
        for index in range(start, len(lines)):
            if lines[index].lstrip(" \t\u2022").startswith("```"):
                end = index
                break
        if end is not None:
            return clean_code_lines(lines[start:end])
    return clean_code_lines(text.splitlines())


def clean_code_lines(lines) -> str:
    stripped = "\n".join(lines).strip()
    dedented = textwrap.dedent(stripped)
    try:
        compile(dedented, "<answer>", "exec")
        return dedented
    except SyntaxError:
        pass

    code_lines = stripped.splitlines()
    if len(code_lines) > 1 and not code_lines[0].startswith((" ", "\t")):
        tail = [line[2:] if line.startswith("  ") else line for line in code_lines[1:]]
        candidate = "\n".join([code_lines[0], *tail])
        try:
            compile(candidate, "<answer>", "exec")
            return candidate
        except SyntaxError:
            pass

    return dedented


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    code = extract_code(read_text_flexible(Path(sys.argv[1])))
    namespace = {}
    try:
        exec(code, namespace)
    except Exception as exc:
        print(json.dumps({
            "benchmark_id": gold["benchmark_id"],
            "task_id": gold["task_id"],
            "hard_score": 0.0,
            "passed": 0,
            "total": len(gold["checks"]),
            "error": f"code_exec_failed: {exc}",
            "checks": [],
        }, ensure_ascii=False, indent=2))
        return 1

    checks = []
    for spec in gold["checks"]:
        fn_name = spec["function"]
        fn = namespace.get(fn_name)
        if not callable(fn):
            checks.append({
                "function": fn_name,
                "passed": False,
                "expected": spec["expected"],
                "actual": None,
                "reason": "missing_function",
            })
            continue

        try:
            actual = fn(*spec["args"])
            actual_float = float(actual)
        except Exception as exc:
            checks.append({
                "function": fn_name,
                "passed": False,
                "expected": spec["expected"],
                "actual": None,
                "reason": f"call_failed: {exc}",
            })
            continue

        expected = float(spec["expected"])
        abs_error = abs(actual_float - expected)
        rel_error = abs_error / abs(expected) if expected != 0 else abs_error
        passed = math.isclose(
            actual_float,
            expected,
            rel_tol=float(spec["rel_tol"]),
            abs_tol=float(spec["abs_tol"]),
        )
        checks.append({
            "function": fn_name,
            "args": spec["args"],
            "passed": bool(passed),
            "expected": expected,
            "actual": actual_float,
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
