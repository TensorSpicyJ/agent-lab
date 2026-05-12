"""
Change Attribution — evaluate whether harness changes actually improved things.

After each iteration, cross-reference the previous change_manifest.json with
actual task score changes to classify each change:

  EFFECTIVE           — predicted tasks improved, no regression
  PARTIALLY_EFFECTIVE — predicted tasks improved, but some regressed
  MIXED               — some improved, some regressed, unclear signal
  INEFFECTIVE         — no significant change in predicted tasks
  HARMFUL             — predicted tasks regressed significantly

This feeds back into the next evolution query so the evolve agent learns
from its own history.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ChangeVerdict:
    """Verdict for a single change from the manifest."""
    change_id: str
    verdict: str          # EFFECTIVE | PARTIALLY_EFFECTIVE | MIXED | INEFFECTIVE | HARMFUL
    description: str
    predicted_fixes: list[str]
    actual_fixes: list[str]
    actual_regressions: list[str]
    score_delta: float
    detail: str


@dataclass
class AttributionReport:
    iteration: int
    verdicts: list[ChangeVerdict] = field(default_factory=list)
    summary: str = ""

    @property
    def effective(self) -> list[ChangeVerdict]:
        return [v for v in self.verdicts if v.verdict in ("EFFECTIVE", "PARTIALLY_EFFECTIVE")]

    @property
    def harmful(self) -> list[ChangeVerdict]:
        return [v for v in self.verdicts if v.verdict == "HARMFUL"]

    @property
    def needs_rollback(self) -> bool:
        """Suggest rollback if harmful changes outweigh effective ones."""
        return len(self.harmful) > len(self.effective)


def evaluate_changes(
    previous_manifest: dict,
    previous_task_scores: dict[str, float],
    current_task_scores: dict[str, float],
    score_threshold: float = 0.03,
) -> AttributionReport:
    """Evaluate how changes from the previous iteration affected task scores.

    Args:
        previous_manifest: The change_manifest.json from the prior evolve step
        previous_task_scores: {task_id: score} from the PREVIOUS evaluation
        current_task_scores: {task_id: score} from the CURRENT evaluation
        score_threshold: Minimum score delta to consider a task as changed

    Returns an AttributionReport with verdicts for each change.
    """
    iteration = previous_manifest.get("iteration", 0)
    report = AttributionReport(iteration=iteration)

    changes = previous_manifest.get("changes", [])
    if not changes:
        report.summary = "No changes to evaluate."
        return report

    # Calculate per-task deltas
    all_tasks = set(list(previous_task_scores) + list(current_task_scores))
    task_deltas = {}
    for tid in all_tasks:
        prev = previous_task_scores.get(tid, 0.0)
        curr = current_task_scores.get(tid, 0.0)
        task_deltas[tid] = curr - prev

    for change in changes:
        change_id = change.get("id", "?")
        predicted = change.get("predicted_fixes", [])
        risk_tasks = change.get("risk_tasks", [])

        # Check which predicted tasks improved
        improved = []
        regressed = []
        for tid in predicted:
            delta = task_deltas.get(tid, 0.0)
            if delta > score_threshold:
                improved.append(tid)
            elif delta < -score_threshold:
                regressed.append(tid)

        # Check which risk tasks regressed
        for tid in risk_tasks:
            delta = task_deltas.get(tid, 0.0)
            if delta < -score_threshold:
                regressed.append(tid)

        avg_delta = sum(task_deltas.get(t, 0.0) for t in predicted) / len(predicted) if predicted else 0.0

        # Classify
        if improved and not regressed:
            verdict = "EFFECTIVE"
        elif improved and regressed:
            verdict = "MIXED"
        elif not improved and regressed:
            verdict = "HARMFUL"
        elif not improved and not regressed:
            verdict = "INEFFECTIVE"
        else:
            verdict = "INEFFECTIVE"

        # Downgrade if predicted tasks show clear improvement but risk tasks regressed
        if verdict == "EFFECTIVE" and regressed:
            verdict = "PARTIALLY_EFFECTIVE"

        detail_parts = []
        if improved:
            detail_parts.append(f"improved: {', '.join(improved)}")
        if regressed:
            detail_parts.append(f"regressed: {', '.join(regressed)}")
        if not improved and not regressed:
            detail_parts.append("no significant impact")
        detail_parts.append(f"avg delta: {avg_delta:+.3f}")

        report.verdicts.append(ChangeVerdict(
            change_id=change_id,
            verdict=verdict,
            description=change.get("description", "no description"),
            predicted_fixes=predicted,
            actual_fixes=improved,
            actual_regressions=regressed,
            score_delta=avg_delta,
            detail="; ".join(detail_parts),
        ))

    # Summary
    counts = {"EFFECTIVE": 0, "PARTIALLY_EFFECTIVE": 0, "MIXED": 0, "INEFFECTIVE": 0, "HARMFUL": 0}
    for v in report.verdicts:
        counts[v.verdict] = counts.get(v.verdict, 0) + 1

    report.summary = (
        f"{len(changes)} changes: "
        + ", ".join(f"{v}×{c}" for v, c in counts.items() if c > 0)
    )
    report.summary += f". Rollback suggested: {report.needs_rollback}"

    return report


def format_attribution_for_query(report: AttributionReport) -> str:
    """Format an attribution report for inclusion in the evolution query."""
    lines = ["## Change Attribution (Previous Iteration)", ""]
    lines.append(report.summary)
    lines.append("")

    for v in report.verdicts:
        emoji = {"EFFECTIVE": "[+]", "PARTIALLY_EFFECTIVE": "[~+]", "MIXED": "[~]", "INEFFECTIVE": "[=]", "HARMFUL": "[-]"}.get(v.verdict, "[?]")
        lines.append(f"### {emoji} {v.change_id}: {v.verdict}")
        lines.append(f"- Description: {v.description}")
        lines.append(f"- Predicted fixes: {v.predicted_fixes or 'none'}")
        lines.append(f"- Actual fixes: {v.actual_fixes or 'none'}")
        lines.append(f"- Regressions: {v.actual_regressions or 'none'}")
        lines.append(f"- Score delta: {v.score_delta:+.3f}")
        lines.append(f"- Detail: {v.detail}")
        lines.append("")

    if report.needs_rollback:
        lines.append("**ACTION**: The previous iteration introduced more harm than good. Consider rolling back the harmful changes before making new ones.")
    elif report.harmful:
        lines.append("**ACTION**: Some changes caused regressions. Revert or revise the harmful ones.")

    return "\n".join(lines)


def save_attribution(report: AttributionReport, output_path: Path):
    """Save attribution report to JSON."""
    data = {
        "iteration": report.iteration,
        "summary": report.summary,
        "needs_rollback": report.needs_rollback,
        "verdicts": [
            {
                "change_id": v.change_id,
                "verdict": v.verdict,
                "description": v.description,
                "predicted_fixes": v.predicted_fixes,
                "actual_fixes": v.actual_fixes,
                "actual_regressions": v.actual_regressions,
                "score_delta": v.score_delta,
                "detail": v.detail,
            }
            for v in report.verdicts
        ],
    }
    output_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
