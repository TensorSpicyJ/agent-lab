import json
import re
import sys
from pathlib import Path


TASK_ID = "wen-kmatrix-multilevel-suite"


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def find_first_failure(attribution):
    failed = attribution.get("failed_checks", [{}])[0]
    cause = attribution.get("candidate_causes", [{}])[0]
    return {
        "failed_check": failed.get("check_id", "unknown"),
        "failed_field": failed.get("failed_field", "unknown"),
        "failure_type": cause.get("failure_type", "unknown"),
    }


def classify_reasoning(reasoning_text: str):
    text = norm(reasoning_text)
    concepts = {
        "source_anyon_vectors": "source_anyon_vectors" in text or "quasiparticles are labeled by integer vectors" in text,
        "source_local_particle_equivalence": "source_local_particle_equivalence" in text or "l ~ l + k n" in text or "local particle" in text,
        "translation_quotient_lattice": "translation_quotient_lattice" in text or "z^n / k z^n" in text or "z^2 / k z^2" in text or "quotient lattice" in text,
        "linear_chain_edge": "source_anyon_vectors → source_local_particle_equivalence" in text or "source_anyon_vectors -> source_local_particle_equivalence" in text,
        "direct_missing_edge": "source_anyon_vectors → translation_quotient_lattice" in text or "source_anyon_vectors -> translation_quotient_lattice" in text,
    }
    matched = [key for key, present in concepts.items() if present]

    if not reasoning_text.strip():
        return "reasoning_unavailable", "No reasoning log was available.", matched, "unknown", "low"

    if concepts["source_anyon_vectors"] and concepts["source_local_particle_equivalence"] and concepts["translation_quotient_lattice"]:
        if concepts["direct_missing_edge"]:
            return (
                "concept_present_but_not_in_final",
                "Reasoning explicitly considers the missing direct edge, but the final JSON omits it. This points to a transfer failure from reasoning to final structured graph, not lack of the physical concept.",
                matched,
                "reasoning_to_final_omission",
                "high",
            )
        if concepts["linear_chain_edge"]:
            return (
                "concept_present_but_serialized_wrong",
                "Reasoning includes the required source concepts and quotient lattice, but serializes them as a linear chain rather than a multi-input merge into the quotient-lattice node.",
                matched,
                "bridge_serialization_error",
                "medium",
            )
        return (
            "concept_present_but_not_in_final",
            "Reasoning includes the required concepts, so the hard failure is likely in transferring the reasoning graph into the final JSON.",
            matched,
            "output_contract_error",
            "medium",
        )

    return (
        "concept_absent",
        "Reasoning does not show all concepts needed for the missing bridge edge.",
        matched,
        "source_extraction_error",
        "medium",
    )


def main():
    if len(sys.argv) not in {4, 5}:
        print("usage: python reasoning_attribution.py <run_id> <failure_attribution.json> <reasoning_stderr.txt> [output.json]")
        return 2

    run_id = sys.argv[1]
    failure_path = Path(sys.argv[2])
    reasoning_path = Path(sys.argv[3])
    failure = load_json(failure_path)
    status, summary, matched, hyp_type, confidence = classify_reasoning(read_text(reasoning_path))

    report = {
        "task_id": TASK_ID,
        "run_id": run_id,
        "hard_failure_ref": find_first_failure(failure),
        "reasoning_source": {
            "path": str(reasoning_path),
            "type": "stderr_reasoning"
        },
        "reasoning_evidence": {
            "status": status,
            "evidence_summary": summary,
            "matched_concepts": matched
        },
        "diagnostic_hypothesis": {
            "type": hyp_type,
            "confidence": confidence,
            "not_hard_score": True
        },
        "score_policy": "diagnostic_only_not_used_for_hard_score",
        "recommended_probe": "Require translation_quotient_lattice to have explicit incoming edges from both source_anyon_vectors and source_local_particle_equivalence; then test whether the agent still serializes them as a chain."
    }

    text = json.dumps(report, ensure_ascii=False, indent=2)
    if len(sys.argv) == 5:
        Path(sys.argv[4]).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
