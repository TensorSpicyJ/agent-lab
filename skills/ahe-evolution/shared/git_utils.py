"""
Git utilities for harness workspace management.

Operations:
  - Initialize workspace as a git repo
  - Commit changes with iteration tags
  - Rollback workspace to a specific commit
  - Snapshot workspace state for reproducibility
"""

import subprocess
from datetime import datetime
from pathlib import Path


def init_workspace(workspace_dir: Path) -> bool:
    """Initialize a git repository in the workspace directory."""
    if (workspace_dir / ".git").exists():
        return True  # Already initialized

    try:
        subprocess.run(
            ["git", "init"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        # Initial empty commit so we can always diff
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial workspace snapshot", "--allow-empty"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git init failed: {e.stderr}")
        return False


def commit_workspace(workspace_dir: Path, message: str, tag: str | None = None) -> str | None:
    """Stage all changes and commit. Optionally tag the commit.
    Returns the commit hash, or None on failure."""
    try:
        subprocess.run(
            ["git", "add", "-A"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", message, "--allow-empty"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        # Get commit hash
        hash_result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        commit_hash = hash_result.stdout.strip()

        if tag:
            subprocess.run(
                ["git", "tag", tag, commit_hash],
                cwd=str(workspace_dir), capture_output=True, text=True, check=True,
            )

        return commit_hash
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed: {e.stderr}")
        return None


def rollback_workspace(workspace_dir: Path, commit_hash: str) -> bool:
    """Rollback workspace to a specific commit, discarding all later changes."""
    try:
        subprocess.run(
            ["git", "reset", "--hard", commit_hash],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git rollback failed: {e.stderr}")
        return False


def snapshot_workspace(workspace_dir: Path, target_dir: Path) -> bool:
    """Copy the current workspace state to a snapshot directory (non-git)."""
    import shutil
    try:
        if target_dir.exists():
            shutil.rmtree(target_dir)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            workspace_dir, target_dir,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
        )
        return True
    except Exception as e:
        print(f"Workspace snapshot failed: {e}")
        return False


def get_current_commit(workspace_dir: Path) -> str | None:
    """Get the current HEAD commit hash."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(workspace_dir), capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None
