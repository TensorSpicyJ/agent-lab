import json
import re
import sys
from pathlib import Path


def extract_json(text: str) -> dict:
    fence = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if fence:
        return json.loads(fence.group(1))

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("No JSON object found in answer")
    return json.loads(text[start : end + 1])


def norm_formula(value: str) -> str:
    return re.sub(r"\s+", "", str(value)).replace("N_v", "Nv").replace("N_p", "Np").replace("N_e", "Ne")


def has_keywords(items, required_groups) -> bool:
    joined = " ".join(str(x).lower() for x in items)
    return all(any(term in joined for term in group) for group in required_groups)


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    answer_path = Path(sys.argv[1])
    raw = answer_path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            text = ""
    if not text:
        raise ValueError("Could not decode answer as UTF-8 or UTF-16")
    data = extract_json(text)

    checks = []

    def check(name, passed, detail=""):
        checks.append({"name": name, "passed": bool(passed), "detail": detail})

    check("task_id", data.get("task_id") == "toric-code-gsd-basic")
    check("final_gsd", data.get("final_gsd") == 4)
    check("encoded_qubits", data.get("encoded_qubits") == 2)
    check("surface", str(data.get("surface", "")).lower() in {"torus", "t2", "genus_1"})

    assumptions = data.get("assumptions", [])
    check(
        "assumptions_keywords",
        isinstance(assumptions, list)
        and len(assumptions) >= 4
        and has_keywords(
            assumptions,
            [
                ["torus", "periodic", "closed"],
                ["edge", "qubit"],
                ["commut", "stabilizer"],
                ["ground", "+1", "eigenspace"],
            ],
        ),
    )

    sc = data.get("stabilizer_counting", {})
    check("qubits_on_edges", sc.get("qubits_on_edges") is True)
    check("star_global_redundancy", sc.get("star_global_redundancy") is True)
    check("plaquette_global_redundancy", sc.get("plaquette_global_redundancy") is True)
    check("independent_stabilizers", norm_formula(sc.get("independent_stabilizers", "")) in {"V+F-2", "Nv+Np-2"})
    check("euler_characteristic", norm_formula(sc.get("euler_characteristic", "")) in {"V-E+F=0", "Nv-Ne+Np=0"})
    check(
        "logical_qubits_formula",
        norm_formula(sc.get("logical_qubits_formula", ""))
        in {"E-(V+F-2)=2", "Ne-(Nv+Np-2)=2"},
    )

    physics = data.get("checks", {})
    check("sphere_gsd", physics.get("sphere_gsd") == 1)
    check("genus_formula", norm_formula(physics.get("genus_formula", "")) in {"4^g", "4**g", "2^(2g)", "2^{2g}"})
    check("logical_loop_algebra", physics.get("logical_loop_algebra") is True)

    caveats = data.get("caveats", {})
    check("no_novelty_claim", caveats.get("no_novelty_claim") is True)
    check("ideal_commuting_projector_exact", caveats.get("ideal_commuting_projector_exact") is True)
    check("perturbative_splitting_exponential", caveats.get("perturbative_splitting_exponential") is True)

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    hard_score = passed / total

    result = {
        "task_id": "toric-code-gsd-basic",
        "hard_score": round(hard_score, 4),
        "passed": passed,
        "total": total,
        "checks": checks,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if hard_score == 1.0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
