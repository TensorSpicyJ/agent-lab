"""
Auto-Rollback — restore workspace to best-known state on regression.

When quality drops significantly from the best-ever score, automatically
roll back the workspace to the best iteration's commit. This prevents
the evolution loop from drifting into worse states.
"""

import json
import subprocess
from pathlib import Path


# ═══════════════════════════════════════════════════════
# Best-Ever Tracking
# ═══════════════════════════════════════════════════════

def load_best_ever(exp_dir: Path) -> dict:
    """Load best-ever tracking data. Returns {best_score, best_iteration, best_commit}."""
    best_file = exp_dir / "best_ever.json"
    if best_file.exists():
        return json.loads(best_file.read_text(encoding="utf-8"))
    return {"best_score": 0.0, "best_iteration": 0, "best_commit": None}


def save_best_ever(exp_dir: Path, score: float, iteration: int, commit: str | None = None):
    """Save best-ever tracking data if current score exceeds best."""
    current = load_best_ever(exp_dir)
    if score > current["best_score"]:
        data = {
            "best_score": score,
            "best_iteration": iteration,
            "best_commit": commit,
        }
        with open(exp_dir / "best_ever.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True
    return False


# ═══════════════════════════════════════════════════════
# Rollback
# ═══════════════════════════════════════════════════════

def should_rollback(
    current_score: float,
    best_score: float,
    relative_threshold: float = 0.05,
    absolute_threshold: float = 0.03,
) -> bool:
    """Determine if rollback is warranted.

    Returns True if:
      - current score is below best by more than relative_threshold (e.g. 5%)
      - AND the absolute drop exceeds absolute_threshold (e.g. 0.03)

    This prevents rollback on noise-level fluctuations while catching
    real regressions.
    """
    if best_score <= 0.0:
        return False

    relative_drop = (best_score - current_score) / best_score
    absolute_drop = best_score - current_score

    return relative_drop > relative_threshold and absolute_drop > absolute_threshold


def rollback_workspace(
    workspace_dir: Path,
    target_commit: str | None = None,
    best_ever: dict | None = None,
) -> dict:
    """Rollback workspace to a specific commit or best-ever state.

    Returns:
        {"rolled_back": bool, "commit": str, "message": str}
    """
    if target_commit:
        commit = target_commit
    elif best_ever and best_ever.get("best_commit"):
        commit = best_ever["best_commit"]
    else:
        # Fallback: revert to initial commit
        try:
            result = subprocess.run(
                ["git", "rev-list", "--max-parents=0", "HEAD"],
                cwd=str(workspace_dir), capture_output=True, text=True, check=True,
            )
            commit = result.stdout.strip()
        except subprocess.CalledProcessError:
            return {"rolled_back": False, "commit": None, "message": "Could not find initial commit"}

    if not commit:
        return {"rolled_back": False, "commit": None, "message": "No target commit specified"}

    # Verify commit exists
    try:
        subprocess.run(
            ["git", "cat-file", "-e", commit],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError:
        return {"rolled_back": False, "commit": commit, "message": f"Commit {commit[:8]} not found"}

    # Perform rollback
    try:
        result = subprocess.run(
            ["git", "reset", "--hard", commit],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        return {
            "rolled_back": True,
            "commit": commit,
            "message": f"Rolled back to {commit[:8]}",
        }
    except subprocess.CalledProcessError as e:
        return {
            "rolled_back": False,
            "commit": commit,
            "message": f"Rollback failed: {e.stderr}",
        }


def check_and_rollback(
    workspace_dir: Path,
    exp_dir: Path,
    current_score: float,
    current_iteration: int,
    current_commit: str | None = None,
) -> dict:
    """Check if rollback needed and perform it.

    Returns {"rolled_back": bool, "message": str, "commit": str}
    """
    best_ever = load_best_ever(exp_dir)

    if not should_rollback(current_score, best_ever.get("best_score", 0.0)):
        # Update best-ever if improved
        improved = save_best_ever(exp_dir, current_score, current_iteration, current_commit)
        return {"rolled_back": False, "improved": improved, "message": "No rollback needed"}

    # Rollback needed
    result = rollback_workspace(workspace_dir, best_ever=best_ever)
    result["improved"] = False

    if result["rolled_back"]:
        print(f"  [rollback] {result['message']}")
        print(f"  [rollback] Best score: {best_ever['best_score']:.3f} (iter {best_ever['best_iteration']})")

    return result
