import json
import re
import sys
from fractions import Fraction
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
PARAMS_PATH = TASK_DIR / "private" / "params.hidden.json"


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


def matmul(A, B):
    rows, inner, cols = len(A), len(B), len(B[0])
    return [[sum(Fraction(A[i][k]) * Fraction(B[k][j]) for k in range(inner)) for j in range(cols)] for i in range(rows)]


def transpose(A):
    return [list(row) for row in zip(*A)]


def inv2(A):
    a, b = map(Fraction, A[0])
    c, d = map(Fraction, A[1])
    det = a * d - b * c
    return [[d / det, -b / det], [-c / det, a / det]]


def vec_col(v):
    return [[Fraction(x)] for x in v]


def col_vec(C):
    return [row[0] for row in C]


def dot(a, b):
    return sum(Fraction(x) * Fraction(y) for x, y in zip(a, b))


def frac_str(x):
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def to_int_matrix(M):
    out = []
    for row in M:
        out_row = []
        for x in row:
            x = Fraction(x)
            if x.denominator != 1:
                raise ValueError(f"Expected integer matrix entry, got {x}")
            out_row.append(x.numerator)
        out.append(out_row)
    return out


def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    answer = extract_json(read_text_flexible(Path(sys.argv[1])))
    K, t, W = params["K"], params["t"], params["W"]

    K_prime = to_int_matrix(matmul(matmul(transpose(W), K), W))
    t_prime = col_vec(matmul(transpose(W), vec_col(t)))

    K_inv = inv2(K)
    Kp_inv = inv2(K_prime)
    nu = dot(t, col_vec(matmul(K_inv, vec_col(t))))
    nu_prime = dot(t_prime, col_vec(matmul(Kp_inv, vec_col(t_prime))))

    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("task_id", answer.get("task_id") == params["task_id"])
    check("derivation_claim", answer.get("derivation_claim") == "nu_prime = nu")
    check("K_prime", answer.get("K_prime") == K_prime, f"expected {K_prime}")
    check("t_prime", answer.get("t_prime") == t_prime, f"expected {t_prime}")
    check("nu", answer.get("nu") == frac_str(nu), f"expected {frac_str(nu)}")
    check("nu_prime", answer.get("nu_prime") == frac_str(nu_prime), f"expected {frac_str(nu_prime)}")
    check("invariant", answer.get("invariant") is True and nu == nu_prime)
    check("no_novelty_claim", answer.get("no_novelty_claim") is True)
    check("source_excerpt_used", answer.get("source_excerpt_used") == "wen-kmatrix-basis-transform-minimal")

    steps = answer.get("steps", [])
    check("steps_is_list", isinstance(steps, list) and len(steps) >= 4)
    rules = [s.get("rule") for s in steps if isinstance(s, dict)]
    allowed = set(params["allowed_rules"])
    required = set(params["required_rules"])
    check("rules_allowed", all(r in allowed for r in rules), f"rules={rules}")
    check("required_rules_present", required.issubset(set(rules)), f"missing={sorted(required - set(rules))}")
    step_ids = {s.get("id") for s in steps if isinstance(s, dict)}
    deps_ok = True
    for step in steps:
        if not isinstance(step, dict):
            deps_ok = False
            continue
        for dep in step.get("depends_on", []):
            if dep and dep not in step_ids and not str(dep).startswith("source:"):
                deps_ok = False
    check("dependency_references_valid", deps_ok)

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
