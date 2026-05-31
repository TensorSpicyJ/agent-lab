import json
import re
import sys
from pathlib import Path


TASK_ID = "band-effective-mass-assumption-gate"
SOURCE_ID = "tight-binding-effective-mass-minimal"


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def extract_json(text: str) -> dict:
    matches = re.findall(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return json.loads(matches[-1])
    return json.loads(text[text.find("{") : text.rfind("}") + 1])


def expand_ledger(card_ledger, steps):
    expanded = []
    for item in card_ledger:
        step_ids = [
            step.get("id")
            for step in steps
            if isinstance(step, dict) and item.get("id") in step.get("depends_on", [])
        ]
        if not step_ids:
            step_ids = ["final_answer"]
        expanded.append({
            "id": item["id"],
            "kind": item["kind"],
            "claim": item["claim"],
            "status": item["status"],
            "support": {
                "source_type": "source_excerpt",
                "source_ref": SOURCE_ID,
                "quote_or_summary": "Task source packet defines effective mass as a local expansion and rejects global small-ka use."
            },
            "scope": {
                "applies_to": step_ids,
                "valid_when": item.get("valid_when", ""),
                "invalid_when": item.get("invalid_when", "")
            },
            "checks": [
                {
                    "check_type": "source_consistency",
                    "status": "not_checked",
                    "detail": "Expanded from compact answer card; hard verifier checks the compact fields separately."
                }
            ]
        })
    return expanded


def main():
    if len(sys.argv) not in {2, 3}:
        print("usage: python normalize_answer_card.py <answer.md> [output.json]")
        return 2

    card = extract_json(read_text(Path(sys.argv[1])))
    record = {
        "task_id": TASK_ID,
        "claim": card.get("claim", ""),
        "physical_premises": [
            {
                "id": "P1",
                "statement": "The dispersion is E(k)=E0-2*t*cos(k*a) with t>0.",
                "source_ref": "prompt"
            },
            {
                "id": "P2",
                "statement": "Effective mass is a local approximation near a specified extremum k0.",
                "source_ref": SOURCE_ID
            },
            {
                "id": "P3",
                "statement": "The task does not specify a low-energy regime, expansion point, or global |k*a| << 1.",
                "source_ref": "prompt"
            }
        ],
        "formal_translations": [
            {
                "id": "T1",
                "physical_object": "one-dimensional tight-binding band",
                "formal_object": "E(k)=E0-2*t*cos(k*a)",
                "status": "given",
                "conventions": ["t>0", "a is lattice spacing"],
                "depends_on": ["P1"]
            },
            {
                "id": "T2",
                "physical_object": "local effective mass",
                "formal_object": "m*=hbar^2/E''(k0)",
                "status": "given",
                "conventions": ["local expansion near specified k0"],
                "depends_on": ["P2"]
            }
        ],
        "assumption_ledger": expand_ledger(card.get("assumption_ledger", []), card.get("steps", [])),
        "derivation_trace": [
            {
                "id": step["id"],
                "statement": step["statement"],
                "rule": step["rule"],
                "depends_on": step.get("depends_on", [])
            }
            for step in card.get("steps", [])
        ],
        "verification_checks": [
            {
                "id": "V1",
                "check_type": "assumption_gate",
                "status": "not_checked",
                "detail": "Expanded record generated from answer card. Run verify_short.py for hard checks."
            }
        ],
        "final_answer": card.get("final_answer", {})
    }

    text = json.dumps(record, ensure_ascii=False, indent=2)
    if len(sys.argv) == 3:
        Path(sys.argv[2]).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
