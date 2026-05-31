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


def frac_str(value: Fraction) -> str:
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def inv_1x1(K):
    if len(K) != 1 or len(K[0]) != 1:
        raise ValueError("This v0 task supports only 1x1 K matrices")
    return [[Fraction(1, K[0][0])]]


def dot(a, b):
    return sum(Fraction(x) * Fraction(y) for x, y in zip(a, b))


def mat_vec(M, v):
    return [sum(M[i][j] * Fraction(v[j]) for j in range(len(v))) for i in range(len(M))]


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    answer = extract_json(read_text_flexible(Path(sys.argv[1])))

    K = params["K"]
    t = params["t"]
    genus = params["genus"]
    l_vectors = params["l_vectors"]
    K_inv = inv_1x1(K)
    det_K = K[0][0]
    abs_det = abs(det_K)
    filling = dot(t, mat_vec(K_inv, t))

    expected_quasiparticles = []
    for l in l_vectors:
        charge = dot(t, mat_vec(K_inv, l))
        theta = dot(l, mat_vec(K_inv, l))
        expected_quasiparticles.append({
            "l": l,
            "charge": frac_str(charge),
            "exchange_statistics_theta_over_pi": frac_str(theta),
        })

    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("task_id", answer.get("task_id") == params["task_id"])
    check("det_K", answer.get("det_K") == det_K)
    check("filling_fraction", answer.get("filling_fraction") == frac_str(filling))
    check("torus_gsd", answer.get("torus_gsd") == abs_det)
    check("genus_gsd", answer.get("genus_gsd") == abs_det ** genus)
    check("no_novelty_claim", answer.get("no_novelty_claim") is True)
    check("source_excerpt_used", answer.get("source_excerpt_used") == "wen-kmatrix-formulas-minimal")

    qp = answer.get("quasiparticles", [])
    check("quasiparticle_count", len(qp) == len(expected_quasiparticles))
    for i, expected in enumerate(expected_quasiparticles):
        actual = qp[i] if i < len(qp) else {}
        check(f"qp_{i}_l", actual.get("l") == expected["l"])
        check(f"qp_{i}_charge", actual.get("charge") == expected["charge"])
        check(
            f"qp_{i}_exchange_statistics",
            actual.get("exchange_statistics_theta_over_pi") == expected["exchange_statistics_theta_over_pi"],
        )

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    result = {
        "task_id": params["task_id"],
        "hard_score": round(passed / total, 4),
        "passed": passed,
        "total": total,
        "checks": checks,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
