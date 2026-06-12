import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


MODES = ["default_on", "all_default_on_flags_off"]
MODE_LABELS = {
    "default_on": "experimental_default_on",
    "all_default_on_flags_off": "experimental_flags_off",
}

SUCCESS_NOTES = {
    ("default_on", 6): ("capability", "Commutation reasoning for N, S^z, and eta^2; no gold-file evidence."),
    ("all_default_on_flags_off", 6): ("capability", "Same stable commutation result as ON."),
    ("default_on", 22): ("format_sensitive", "Answered N_k B. OFF answered f = N_k B, which is physically equivalent but fails the strict expected form."),
    ("default_on", 26): ("capability", "Magnetic-translation/gauge-invariance reasoning led to b;c;e; OFF timed out."),
    ("default_on", 27): ("capability_with_parameter_cue", "Derived O_n = E_n - E_{n-1}; listed parameters strongly constrain the form."),
    ("all_default_on_flags_off", 27): ("capability_with_parameter_cue", "Same derivation as ON; parameters strongly constrain the form."),
    ("default_on", 49): ("capability", "Long SU(2) and C4 representation-counting trace; OFF timed out."),
    ("all_default_on_flags_off", 5): ("uncertain_capability", "Reasoned about TBG symmetries, but the tool trace says the prompt line looked truncated."),
    ("all_default_on_flags_off", 16): ("capability_low_confidence", "Long Hubbard-ring reasoning with explicit uncertainty; final a;d matched verifier."),
    ("all_default_on_flags_off", 36): ("capability", "Kitaev/PEPS operator mapping reasoning led to a;b."),
}


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def mode_paths(run_root, mode):
    return {
        "summary": run_root / "scores" / f"cmt-hard-research-50.{mode}.summary.json",
        "score": run_root / "scores" / f"cmt-hard-research-50.{mode}.full-score.json",
        "output": run_root / "outputs" / f"cmt-hard-research-50.{mode}.json",
    }


def load_mode(run_root, mode):
    paths = mode_paths(run_root, mode)
    summary = load_json(paths["summary"])
    score = load_json(paths["score"])
    output = load_json(paths["output"])
    runs = {item["problem_number"]: item for item in summary["item_runs"]}
    return {"summary": summary, "score": score, "output": output, "runs": runs}


def classify_single_failure(check, run_item):
    if run_item["status"] != "completed" or not run_item.get("captured_json"):
        return "runtime_timeout_no_json"
    check_type = check["type"]
    if check_type == "choice_set":
        expected = set(check.get("expected", []))
        actual = set(check.get("actual_parsed", []))
        if actual > expected:
            return "choice_over_selected"
        if actual < expected:
            return "choice_under_selected"
        return "choice_wrong_set"
    if check_type == "numeric_vector":
        expected = check.get("expected", [])
        actual = check.get("actual_parsed", [])
        if len(actual) != len(expected):
            return "numeric_wrong_length"
        return "numeric_value_mismatch"
    if check_type == "symbolic":
        actual_norm = check.get("actual_normalized", "")
        expected_norm = check.get("expected_normalized", "")
        if expected_norm and expected_norm in actual_norm and actual_norm != expected_norm:
            return "symbolic_format_or_extra_lhs"
        return "symbolic_formula_mismatch"
    return "unknown_failure"


def pair_category(on_check, off_check, on_run, off_run, on_value, off_value):
    on_pass = bool(on_check.get("passed"))
    off_pass = bool(off_check.get("passed"))
    on_cap = bool(on_run.get("captured_json"))
    off_cap = bool(off_run.get("captured_json"))
    if on_pass and off_pass:
        return "both_pass"
    if on_pass and not off_pass:
        return "on_only_pass"
    if off_pass and not on_pass:
        return "off_only_pass"
    if not on_cap and not off_cap:
        return "both_timeout_or_no_answer"
    if not on_cap and off_cap:
        return "on_no_answer_off_wrong"
    if on_cap and not off_cap:
        return "off_no_answer_on_wrong"
    if on_value == off_value:
        return "both_wrong_same_answer"
    return "both_wrong_different_answer"


def build_report(run_root):
    metadata = load_json(run_root / "run-metadata.json")
    gold = load_json(run_root.parents[1] / "tasks" / "cmt-hard-research-50" / "private" / "gold.json")
    modes = {mode: load_mode(run_root, mode) for mode in MODES}

    mode_summaries = {}
    for mode, data in modes.items():
        summary = data["summary"]
        status_counts = Counter(item["status"] for item in summary["item_runs"])
        mode_summaries[mode] = {
            "label": MODE_LABELS[mode],
            "passed": summary["passed"],
            "total": summary["total"],
            "hard_score": summary["hard_score"],
            "valid_json": sum(1 for item in summary["item_runs"] if item.get("captured_json")),
            "timeouts_or_no_answer": sum(1 for item in summary["item_runs"] if not item.get("captured_json")),
            "status_counts": dict(sorted(status_counts.items())),
            "passed_problems": [
                idx + 1 for idx, check in enumerate(data["score"]["checks"]) if check.get("passed")
            ],
            "timeout_problems": [
                item["problem_number"] for item in summary["item_runs"] if item["status"] != "completed"
            ],
        }

    per_problem = []
    pair_counts = Counter()
    pair_items = defaultdict(list)
    failure_counts = {mode: Counter() for mode in MODES}
    success_reviews = []

    for idx, gold_check in enumerate(gold["checks"], start=1):
        field = gold_check["field"]
        on = modes["default_on"]
        off = modes["all_default_on_flags_off"]
        on_check = on["score"]["checks"][idx - 1]
        off_check = off["score"]["checks"][idx - 1]
        on_run = on["runs"][idx]
        off_run = off["runs"][idx]
        on_value = on["output"].get(field)
        off_value = off["output"].get(field)

        category = pair_category(on_check, off_check, on_run, off_run, on_value, off_value)
        pair_counts[category] += 1
        pair_items[category].append(idx)

        mode_records = {}
        for mode, data, check, run_item, value in [
            ("default_on", on, on_check, on_run, on_value),
            ("all_default_on_flags_off", off, off_check, off_run, off_value),
        ]:
            failure_reason = None
            success_review = None
            if check.get("passed"):
                success_review = SUCCESS_NOTES.get((mode, idx), ("capability_unreviewed", "Passed verifier; no gold-file leakage found in log scan."))
                success_reviews.append(
                    {
                        "mode": mode,
                        "problem": idx,
                        "field": field,
                        "review": success_review[0],
                        "note": success_review[1],
                    }
                )
            else:
                failure_reason = classify_single_failure(check, run_item)
                failure_counts[mode][failure_reason] += 1
            mode_records[mode] = {
                "passed": bool(check.get("passed")),
                "status": run_item["status"],
                "captured_json": bool(run_item.get("captured_json")),
                "runtime_seconds": run_item["runtime_seconds"],
                "actual_raw": check.get("actual_raw"),
                "actual_parsed": check.get("actual_parsed"),
                "failure_reason": failure_reason,
                "success_review": success_review[0] if success_review else None,
            }

        per_problem.append(
            {
                "problem": idx,
                "field": field,
                "type": gold_check["type"],
                "expected": gold_check.get("expected"),
                "pair_category": category,
                "default_on": mode_records["default_on"],
                "all_default_on_flags_off": mode_records["all_default_on_flags_off"],
            }
        )

    return {
        "created_at": datetime.now().astimezone().isoformat(),
        "run_root": str(run_root),
        "run_id": metadata["run_id"],
        "started_at": metadata["started_at"],
        "finished_at": metadata["finished_at"],
        "model_alias": metadata["model_alias"],
        "mode_summaries": mode_summaries,
        "pair_category_counts": dict(pair_counts),
        "pair_category_items": {key: pair_items[key] for key in sorted(pair_items)},
        "failure_counts": {mode: dict(counts) for mode, counts in failure_counts.items()},
        "success_reviews": success_reviews,
        "leakage_scan": {
            "gold_file_mentions": 0,
            "private_file_mentions": 0,
            "note": "Manual Select-String scan found no gold.json/private/sample.correct leakage in logs; some prompts expose Parameters lists that can cue answer format.",
        },
        "per_problem": per_problem,
    }


def join_items(items):
    if not items:
        return "-"
    return ", ".join(f"{item:02d}" for item in items)


def render_md(report):
    mode_summaries = report["mode_summaries"]
    pair_items = report["pair_category_items"]
    lines = []
    lines.append("# Hakimi CMT50 ON/OFF Doing-Difference Audit")
    lines.append("")
    lines.append(f"- Run: `{report['run_id']}`")
    lines.append(f"- Model: `{report['model_alias']}`")
    lines.append(f"- Window: `{report['started_at']}` to `{report['finished_at']}`")
    lines.append("")
    lines.append("## Score")
    lines.append("")
    lines.append("| Mode | Correct | Valid JSON | Timeout/no answer | Passed problems |")
    lines.append("|---|---:|---:|---:|---|")
    for mode in MODES:
        summary = mode_summaries[mode]
        lines.append(
            f"| {summary['label']} | {summary['passed']}/{summary['total']} | "
            f"{summary['valid_json']}/{summary['total']} | {summary['timeouts_or_no_answer']} | "
            f"{join_items(summary['passed_problems'])} |"
        )
    lines.append("")
    lines.append("## Doing Difference")
    lines.append("")
    lines.append("| Category | Count | Problems |")
    lines.append("|---|---:|---|")
    category_order = [
        "both_pass",
        "on_only_pass",
        "off_only_pass",
        "both_wrong_same_answer",
        "both_wrong_different_answer",
        "on_no_answer_off_wrong",
        "off_no_answer_on_wrong",
        "both_timeout_or_no_answer",
    ]
    labels = {
        "both_pass": "Both correct",
        "on_only_pass": "ON correct only",
        "off_only_pass": "OFF correct only",
        "both_wrong_same_answer": "Both wrong, same answer",
        "both_wrong_different_answer": "Both wrong, different answers",
        "on_no_answer_off_wrong": "ON no answer, OFF wrong",
        "off_no_answer_on_wrong": "OFF no answer, ON wrong",
        "both_timeout_or_no_answer": "Both timeout/no answer",
    }
    counts = report["pair_category_counts"]
    for key in category_order:
        items = pair_items.get(key, [])
        lines.append(f"| {labels[key]} | {counts.get(key, 0)} | {join_items(items)} |")
    lines.append("")
    lines.append("## Error Attribution")
    lines.append("")
    lines.append("| Mode | Failure reason | Count |")
    lines.append("|---|---|---:|")
    for mode in MODES:
        for reason, count in sorted(report["failure_counts"][mode].items()):
            lines.append(f"| {MODE_LABELS[mode]} | {reason} | {count} |")
    lines.append("")
    lines.append("## Success Review")
    lines.append("")
    lines.append("| Mode | Problem | Review | Note |")
    lines.append("|---|---:|---|---|")
    for item in report["success_reviews"]:
        lines.append(
            f"| {MODE_LABELS[item['mode']]} | {item['problem']:02d} | "
            f"{item['review']} | {item['note']} |"
        )
    lines.append("")
    lines.append("## Audit Notes")
    lines.append("")
    lines.append("- No gold/private/sample-correct file leakage was found in the log scan.")
    lines.append("- Several prompts expose a `Parameters` list; that can cue output variables or answer format, especially for choice-set items.")
    lines.append("- Problem 22 is a verifier-format sensitivity case: OFF gave `f = N_k B`, while the verifier expected only `N_k B`.")
    lines.append("- The total score is tied, but ON produced more valid answers and fewer timeouts.")
    lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-root", required=True)
    parser.add_argument("--out-prefix", default="HAKIMI-CMT50-ONOFF-DOING-DIFFERENCE-2026-06-06")
    args = parser.parse_args()

    run_root = Path(args.run_root)
    report = build_report(run_root)
    out_json = run_root.parents[1] / f"{args.out_prefix}.json"
    out_md = run_root.parents[1] / f"{args.out_prefix}.md"
    out_json.write_text(json.dumps(report, indent=2, ensure_ascii=True), encoding="utf-8")
    out_md.write_text(render_md(report), encoding="utf-8")
    print(out_json)
    print(out_md)


if __name__ == "__main__":
    main()
