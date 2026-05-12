"""
Git Worktree Sandbox — isolated execution environment for research tasks.

Each task runs in its own sandbox directory with:
  - A copy of the harness (systemprompt, tools, middleware, skills)
  - A copy of the knowledge layer (for research context)
  - Path sandboxing (../ escapes blocked)
"""

import os
import shutil
import tempfile
from pathlib import Path


class Sandbox:
    """An isolated directory sandbox for running a single research task.

    The sandbox contains:
      sandbox_root/
        ├── harness/       ← copy of agent harness
        ├── knowledge/     ← copy of knowledge layer
        └── workspace/     ← agent writes outputs here
    """

    def __init__(
        self,
        harness_dir: Path,
        knowledge_dir: Path,
        sandbox_root: Path | None = None,
    ):
        """
        Args:
            harness_dir: Path to the harness source directory
            knowledge_dir: Path to the knowledge layer
            sandbox_root: Where to create the sandbox (None = auto temp dir)
        """
        self.harness_dir = Path(harness_dir).resolve()
        self.knowledge_dir = Path(knowledge_dir).resolve()
        self.root = Path(sandbox_root) if sandbox_root else Path(tempfile.mkdtemp(prefix="ahe-sandbox-"))
        self._active = False

    def setup(self) -> Path:
        """Create the sandbox directory and copy harness + knowledge into it."""
        if self._active:
            return self.root

        self.root.mkdir(parents=True, exist_ok=True)

        # Copy harness
        harness_target = self.root / "harness"
        _copy_tree(self.harness_dir, harness_target)

        # Copy knowledge layer
        knowledge_target = self.root / "knowledge"
        _copy_tree(self.knowledge_dir, knowledge_target)

        # Create workspace for agent outputs
        workspace = self.root / "workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        self._active = True
        return self.root

    def cleanup(self):
        """Remove the sandbox directory."""
        if self.root.exists():
            shutil.rmtree(self.root, ignore_errors=True)
        self._active = False

    def resolve(self, path: str) -> Path:
        """Resolve a relative path to an absolute path inside the sandbox.
        Blocks path traversal attacks (../ escapes)."""
        p = (self.root / path).resolve()
        if self.root not in p.parents and p != self.root.resolve():
            raise PermissionError(f"Path escapes sandbox: {path}")
        return p

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, *args):
        self.cleanup()


def _copy_tree(src: Path, dst: Path):
    """Copy a directory tree, skipping __pycache__ and .git directories."""
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        if item.name in ("__pycache__", ".git", ".gitignore", "*.pyc"):
            continue
        target = dst / item.name
        if item.is_dir():
            _copy_tree(item, target)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
