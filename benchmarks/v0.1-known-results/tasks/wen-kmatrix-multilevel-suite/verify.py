import json
import re
import sys
from pathlib import Path


TASK_DIR = Path(__file__).resolve().parent
PARAMS_PATH = TASK_DIR / "private" / "params.hidden.json"


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
    return re.sub(r"[\s{}_\-\*×x]+", "", str(x or "").lower())


def same_frac(observed, expected):
    return norm(observed) == norm(expected)


def as_tuple(v):
    return tuple(int(x) for x in v)


def det2(K):
    return K[0][0] * K[1][1] - K[0][1] * K[1][0]


def mod_image_class(vec, K):
    # For K=[[2,1],[1,2]], quotient is Z_3 and x-y mod 3 is a class invariant.
    return (vec[0] - vec[1]) % abs(det2(K))


def main():
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    params = json.loads(PARAMS_PATH.read_text(encoding="utf-8"))
    expected = params["expected"]
    answer = extract_json(read_text(Path(sys.argv[1])))
    checks = []

    def check(level, name, passed, detail=""):
        checks.append({
            "level": level,
            "name": name,
            "passed": bool(passed),
            "detail": detail,
        })

    check("contract", "task_id", answer.get("task_id") == params["task_id"])
    check("contract", "source_excerpt_used", answer.get("source_excerpt_used") == "wen-kmatrix-multilevel-minimal")

    l1 = answer.get("level_1", {})
    check("level_1", "det_K", l1.get("det_K") == expected["det_K"])
    check("level_1", "filling_fraction", same_frac(l1.get("filling_fraction"), expected["filling_fraction"]))
    check("level_1", "torus_gsd", l1.get("torus_gsd") == expected["torus_gsd"])
    check("level_1", "genus_gsd", l1.get("genus_gsd") == expected["genus_gsd"])
    charges = l1.get("charges", {})
    stats = l1.get("statistics_theta_over_pi", {})
    for key, value in expected["charges"].items():
        check("level_1", f"charge_{key}", same_frac(charges.get(key), value))
    for key, value in expected["statistics_theta_over_pi"].items():
        check("level_1", f"theta_{key}", same_frac(stats.get(key), value))

    l2 = answer.get("level_2", {})
    check("level_2", "anyon_lattice", norm(l2.get("anyon_lattice")) in {"z2/kz2", "z^2/kz^2", "z2modkz2"})
    check("level_2", "snf_invariant_factors", l2.get("snf_invariant_factors") == expected["snf_invariant_factors"])
    check("level_2", "quotient_group", norm(l2.get("quotient_group")) in {"z3", "z/3z", "z_3"})
    reps = l2.get("representatives", [])
    rep_ok = isinstance(reps, list) and len(reps) == 3
    if rep_ok:
        try:
            classes = {mod_image_class(as_tuple(r), params["K"]) for r in reps}
            rep_ok = classes == {0, 1, 2}
        except Exception:
            rep_ok = False
    check("level_2", "representatives_cover_three_classes", rep_ok, f"representatives={reps}")
    steps = l2.get("derivation_steps", [])
    rules = {s.get("rule") for s in steps if isinstance(s, dict)}
    check("level_2", "required_derivation_rules", {"local_particle_quotient", "smith_normal_form_or_index", "torus_sector_count"}.issubset(rules), f"rules={sorted(rules)}")

    l3 = answer.get("level_3", {})
    node_ids = {n.get("id") for n in l3.get("nodes", []) if isinstance(n, dict)}
    required_nodes = set(params["required_bridge_nodes"])
    check("level_3", "required_nodes_present", required_nodes.issubset(node_ids), f"missing={sorted(required_nodes - node_ids)}")
    edges = {tuple(e) for e in l3.get("edges", []) if isinstance(e, list) and len(e) == 2}
    required_edges = {tuple(e) for e in params["required_bridge_edges"]}
    check("level_3", "required_edges_present", required_edges.issubset(edges), f"missing={sorted(required_edges - edges)}")
    check("level_3", "final_claim", "gsd" in norm(l3.get("final_claim")) and "detk" in norm(l3.get("final_claim")))

    l4 = answer.get("level_4", {})
    links = {(link.get("from"), link.get("to")) for link in l4.get("section_links", []) if isinstance(link, dict)}
    required_links = {tuple(x) for x in params["required_section_links"]}
    check("level_4", "section_links_present", required_links.issubset(links), f"missing={sorted(required_links - links)}")
    edge = l4.get("edge", {})
    for key, value in expected["edge"].items():
        check("level_4", f"edge_{key}", edge.get(key) == value, f"expected={value}")
    check("level_4", "bulk_edge_connection_is_physical_bridge", edge.get("bulk_edge_connection_is_physical_bridge") is True)

    control = answer.get("claim_control", {})
    check("claim_control", "no_novelty_claim", control.get("no_novelty_claim") is True)
    check("claim_control", "does_not_claim_real_material_identification", control.get("does_not_claim_real_material_identification") is True)

    passed = sum(1 for c in checks if c["passed"])
    total = len(checks)
    by_level = {}
    for c in checks:
        stats = by_level.setdefault(c["level"], {"passed": 0, "total": 0})
        stats["total"] += 1
        stats["passed"] += int(c["passed"])
    for stats in by_level.values():
        stats["score"] = round(stats["passed"] / stats["total"], 4)

    print(json.dumps({
        "task_id": params["task_id"],
        "hard_score": round(passed / total, 4),
        "passed": passed,
        "total": total,
        "by_level": by_level,
        "checks": checks,
    }, ensure_ascii=False, indent=2))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

