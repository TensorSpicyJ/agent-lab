"""
AHE Evolution Loop — Main Orchestrator

Usage:
  python evolve.py --config config/experiments/exp-01-baseline.yaml
  python evolve.py --batch config/experiments/
  python evolve.py --experiment <name> --start-iteration N --config <...>

The main loop: Evaluate → Analyze → Improve → Repeat
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml

# Add skill root to path
SKILL_DIR = Path(__file__).resolve().parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from shared.config_loader import load_config, resolve_output_dir
from shared.git_utils import init_workspace, snapshot_workspace, get_current_commit
from shared.sandbox import Sandbox
from shared.change_attribution import evaluate_changes, format_attribution_for_query, save_attribution
from shared.auto_rollback import check_and_rollback, load_best_ever, save_best_ever


# ═══════════════════════════════════════════════════════
# Experiment Setup
# ═══════════════════════════════════════════════════════

def create_experiment_dir(config: dict) -> Path:
    """Create a timestamped experiment directory under the output dir."""
    output_root = resolve_output_dir(config)
    timestamp = datetime.now().strftime("%Y-%m-%d__%H-%M-%S")
    meta = config.get("_meta", {})
    name = meta.get("_name", "unnamed")
    exp_dir = output_root / f"{timestamp}__{name}"
    exp_dir.mkdir(parents=True, exist_ok=True)
    return exp_dir


def init_workspace_from_source(config: dict, exp_dir: Path) -> Path:
    """Copy harness source to experiment workspace and init git."""
    source_dir = SKILL_DIR / config.get("source_config_dir", "harness")
    workspace_dir = exp_dir / "workspace"

    # Copy harness
    import shutil
    if workspace_dir.exists():
        shutil.rmtree(workspace_dir)
    shutil.copytree(
        source_dir, workspace_dir,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".git"),
    )

    init_workspace(workspace_dir)
    return workspace_dir


def load_tasks(config: dict) -> list[dict]:
    """Load task definitions from tasks.yaml."""
    tasks_path = SKILL_DIR / config.get("tasks_config", "tasks/tasks.yaml")
    with open(tasks_path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data.get("tasks", [])


# ═══════════════════════════════════════════════════════
# Main Loop
# ═══════════════════════════════════════════════════════

def run_single_experiment(
    config: dict,
    config_path: str,
    experiment_name: str | None = None,
    start_iteration: int = 1,
    skip_eval: bool = False,
) -> dict:
    """Run a full AHE evolution experiment."""

    # ── Setup ──
    tasks = load_tasks(config)
    if not tasks:
        print("[evolve] No tasks defined. Aborting.")
        return {"status": "error", "reason": "no tasks"}

    if experiment_name:
        # Resuming existing experiment
        output_root = resolve_output_dir(config)
        exp_dir = output_root / experiment_name
        if not exp_dir.exists():
            print(f"[evolve] Experiment directory not found: {exp_dir}")
            return {"status": "error", "reason": "experiment not found"}
        workspace_dir = exp_dir / "workspace"
    else:
        exp_dir = create_experiment_dir(config)
        workspace_dir = init_workspace_from_source(config, exp_dir)

        # Save config snapshot for reproducibility
        with open(exp_dir / "config_snapshot.yaml", "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True)
        (exp_dir / "evolution_history.md").write_text(
            f"# Evolution History\n\nExperiment started: {datetime.now(timezone.utc).isoformat()}\n\n"
        )

    llm_config = config["llm"]
    eval_cfg = config.get("evaluation", {})
    k_rollouts = eval_cfg.get("k", 1)
    max_turns = eval_cfg.get("max_turns", 15)
    target_quality = config.get("_target_quality", 0.85)
    max_iterations = config.get("max_iterations", 20)
    evolvable = config.get("evolvable_components", {})
    knowledge_dir = SKILL_DIR.parent.parent / "knowledge"  # agent-lab/knowledge

    all_locked = all(not unlocked for unlocked in evolvable.values())
    if all_locked:
        print("[evolve] All components locked — running in analysis-only mode.")

    # ── Iteration Loop ──
    best_score = 0.0
    best_iteration = 0
    scores_history = []
    previous_manifest = None
    previous_task_scores: dict[str, float] = {}
    attribution_text = ""
    rollback_occurred = False

    for iteration in range(start_iteration, max_iterations + 1):
        print(f"\n{'='*60}")
        print(f"  ITERATION {iteration} / {max_iterations}")
        print(f"  Experiment: {exp_dir.name}")
        print(f"  Model: {llm_config.get('model', '?')}")
        print(f"{'='*60}\n")

        iter_dir = exp_dir / "runs" / f"iteration_{iteration:03d}"
        input_dir = iter_dir / "input"
        input_dir.mkdir(parents=True, exist_ok=True)

        # ── Phase 0: Snapshot workspace ──
        snapshot_workspace(workspace_dir, input_dir / "workspace")
        commit_before = get_current_commit(workspace_dir)

        # ── Phase 1: EVALUATE ──
        results_dir = input_dir / "results" / "jobs" / datetime.now().strftime("%Y-%m-%dT%H-%M-%S")

        if not skip_eval:
            print("[Phase 1] EVALUATE — running tasks...")
            from task_runner import run_all_tasks
            task_results = run_all_tasks(
                config=config,
                tasks=tasks,
                harness_dir=workspace_dir,
                knowledge_dir=knowledge_dir,
                results_dir=results_dir,
                k=k_rollouts,
            )
        else:
            print("[Phase 1] SKIP — using existing results")
            task_results = _load_existing_results(results_dir, tasks)

        # Compute aggregate score
        task_scores = {}
        for r in task_results:
            if r and r.get("score"):
                task_scores[r["task_id"]] = r["score"]["overall_score"]

        overall_score = sum(task_scores.values()) / len(task_scores) if task_scores else 0.0
        scores_history.append({"iteration": iteration, "score": overall_score, "task_scores": task_scores})
        print(f"  Overall quality: {overall_score:.3f} (target: {target_quality})")

        # Track best
        if overall_score > best_score:
            best_score = overall_score
            best_iteration = iteration

        # ── Change Attribution (after iteration 1) ──
        if iteration > start_iteration and previous_manifest and previous_task_scores:
            print("  [attribution] Evaluating previous changes...")
            attribution_report = evaluate_changes(
                previous_manifest=previous_manifest,
                previous_task_scores=previous_task_scores,
                current_task_scores=task_scores,
            )
            attribution_text = format_attribution_for_query(attribution_report)
            save_attribution(attribution_report, input_dir / "change_evaluation.json")
            print(f"  [attribution] {attribution_report.summary}")
        else:
            attribution_text = ""

        # ── Auto-Rollback ──
        current_commit = get_current_commit(workspace_dir)
        rollback_result = check_and_rollback(
            workspace_dir=workspace_dir,
            exp_dir=exp_dir,
            current_score=overall_score,
            current_iteration=iteration,
            current_commit=current_commit,
        )
        if rollback_result.get("rolled_back"):
            print(f"  [rollback] Restored workspace to best-known state")
            rollback_occurred = True
            # After rollback, skip further evolution this iteration
            previous_task_scores = dict(task_scores)
            _save_iteration_scores(exp_dir, scores_history)
            continue
        elif rollback_result.get("improved"):
            save_best_ever(exp_dir, overall_score, iteration, current_commit)

        # Save task scores for next iteration's attribution
        previous_task_scores = dict(task_scores)

        # Check termination
        if overall_score >= target_quality:
            print(f"\n[evolve] Target quality {target_quality} reached at iteration {iteration}!")
            break

        # ── Phase 2: ANALYZE ──
        analysis_dir = input_dir / "analysis"
        t0 = time.time()

        print("[Phase 2] ANALYZE — analyzing traces...")
        from trace_analyzer import TraceAnalyzer
        analyzer_config = config.get("trace_analyzer", {})
        use_llm = analyzer_config.get("enabled", True) and llm_config.get("api_key", "")

        analyzer = TraceAnalyzer(llm_config=llm_config if use_llm else None)
        analysis = analyzer.analyze(
            results_dir=results_dir,
            tasks=tasks,
            output_dir=analysis_dir,
        )
        print(f"  Analysis complete in {time.time() - t0:.1f}s")
        print(f"  Overview: {analysis['overview_path']}")

        # ── Phase 3: IMPROVE ──
        evolve_dir = iter_dir / "evolve"
        evolve_dir.mkdir(parents=True, exist_ok=True)

        print("[Phase 3] IMPROVE — evolving harness...")
        from evolve_agent import EvolveAgent
        evolver = EvolveAgent(llm_config=llm_config)

        evolution_history = (exp_dir / "evolution_history.md").read_text(encoding="utf-8")

        # Merge attribution into analysis for evolve agent context
        analysis_with_attribution = analysis.get("overview_text", "")
        if attribution_text:
            analysis_with_attribution += "\n\n" + attribution_text

        evolve_result = evolver.evolve(
            workspace_dir=workspace_dir,
            iteration_dir=iter_dir,
            iteration=iteration,
            analysis_overview=analysis_with_attribution,
            task_results={tid: {"score": ts, "status": "completed"} for tid, ts in task_scores.items()},
            evolution_history=evolution_history,
            previous_manifest=previous_manifest,
            evolvable_components=evolvable,
            dry_run=all_locked,
        )

        previous_manifest = evolve_result.get("manifest")
        print(f"  Changes: {len(previous_manifest.get('changes', []))}")
        print(f"  Commit: {evolve_result.get('commit', 'none')}")

        # Update evolution history
        _append_history(exp_dir, iteration, overall_score, evolve_result)

        # ── Phase 4: Track ──
        _save_iteration_scores(exp_dir, scores_history)

    # ── Done ──
    _save_iteration_scores(exp_dir, scores_history)
    _save_best_ever(exp_dir, best_score, best_iteration)

    print(f"\n{'='*60}")
    print(f"  Experiment complete: {exp_dir.name}")
    print(f"  Best score: {best_score:.3f} (iteration {best_iteration})")
    print(f"  Total iterations: {len(scores_history)}")
    print(f"{'='*60}")

    return {
        "status": "complete",
        "experiment_dir": str(exp_dir),
        "best_score": best_score,
        "best_iteration": best_iteration,
        "total_iterations": len(scores_history),
    }


# ═══════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════

def _load_existing_results(results_dir: Path, tasks: list[dict]) -> list[dict]:
    """Load previously-computed results (for --skip-eval)."""
    results = []
    for task_config in tasks:
        task_id = task_config["id"]
        result_file = results_dir / task_id / "result.json"
        if result_file.exists():
            results.append(json.loads(result_file.read_text(encoding="utf-8")))
        else:
            print(f"  Warning: no existing results for {task_id}")
    return results


def _save_iteration_scores(exp_dir: Path, scores_history: list):
    """Write iteration scores to YAML and Markdown."""
    # YAML
    with open(exp_dir / "iteration_scores.yaml", "w", encoding="utf-8") as f:
        yaml.dump({"scores": scores_history}, f, allow_unicode=True)

    # Markdown
    lines = ["# Iteration Scores", "", "| Iteration | Overall Score | Tasks |", "|-----------|--------------|-------|"]
    for entry in scores_history:
        tasks_str = ", ".join(f"{k}:{v:.2f}" for k, v in entry.get("task_scores", {}).items())
        lines.append(f"| {entry['iteration']} | {entry['score']:.3f} | {tasks_str} |")
    (exp_dir / "iteration_scores.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _save_best_ever(exp_dir: Path, best_score: float, best_iteration: int):
    """Save best-ever tracking."""
    with open(exp_dir / "best_ever.json", "w", encoding="utf-8") as f:
        json.dump({
            "best_score": best_score,
            "best_iteration": best_iteration,
        }, f)


def _append_history(exp_dir: Path, iteration: int, score: float, evolve_result: dict):
    """Append iteration summary to evolution_history.md."""
    manifest = evolve_result.get("manifest", {})
    changes = manifest.get("changes", [])
    changes_text = "\n".join(
        f"  - {c.get('id', '?')}: {c.get('description', 'no description')[:120]}"
        for c in changes
    ) if changes else "  (no changes — all components locked)"

    entry = f"""
### Iteration {iteration}
- **Score**: {score:.3f}
- **Changes**: {len(changes)}
{changes_text}
- **Commit**: {evolve_result.get('commit', 'none')}

"""
    with open(exp_dir / "evolution_history.md", "a", encoding="utf-8") as f:
        f.write(entry)


# ═══════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="AHE Evolution Loop")
    parser.add_argument("--config", help="Config file path (base or overlay with _base)")
    parser.add_argument("--batch", nargs="*", help="Directory or list of experiment overlay files")
    parser.add_argument("--experiment", help="Resume existing experiment (directory name under output)")
    parser.add_argument("--start-iteration", type=int, default=1, help="Start from this iteration")
    parser.add_argument("--skip-eval", action="store_true", help="Skip evaluation, use existing results")
    args = parser.parse_args()

    if args.batch is not None:
        # Batch mode
        paths = args.batch
        if not paths:
            paths = [str(SKILL_DIR / "config" / "experiments")]

        config_files = []
        for p in paths:
            p = Path(p)
            if p.is_dir():
                config_files.extend(sorted(p.glob("*.yaml")))
            else:
                config_files.append(p)

        if not config_files:
            print("[batch] No config files found")
            sys.exit(1)

        for cf in config_files:
            print(f"\n[batch] Running: {cf}")
            config = load_config(str(cf))
            run_single_experiment(config, str(cf))
        return

    # Single experiment mode
    if not args.config:
        parser.error("--config required (or use --batch)")
        sys.exit(1)

    config = load_config(args.config)
    run_single_experiment(
        config=config,
        config_path=args.config,
        experiment_name=args.experiment,
        start_iteration=args.start_iteration,
        skip_eval=args.skip_eval,
    )


if __name__ == "__main__":
    main()
