"""File read/write tools with sandbox path resolution."""

from pathlib import Path


# Injected by task_runner at setup time
_SANDBOX_ROOT: Path | None = None


def _set_sandbox_root(root: Path):
    global _SANDBOX_ROOT
    _SANDBOX_ROOT = root


def _resolve(path: str) -> Path:
    """Resolve a path relative to the sandbox root. Block escapes."""
    if _SANDBOX_ROOT is None:
        raise RuntimeError("Sandbox root not set — call _set_sandbox_root first")
    p = (_SANDBOX_ROOT / path).resolve()
    if _SANDBOX_ROOT not in p.parents and p != _SANDBOX_ROOT.resolve():
        raise PermissionError(f"Path escapes sandbox: {path}")
    return p


def read_file(path: str) -> str:
    """Read file contents. Path is relative to the sandbox root."""
    p = _resolve(path)
    if not p.exists():
        return f"Error: file not found: {path}"
    return p.read_text(encoding="utf-8")


def write_file(path: str, content: str) -> str:
    """Write content to a file. Creates parent directories if needed.
    Verifies the write succeeded by re-reading the file."""
    p = _resolve(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    written = p.read_text(encoding="utf-8")
    if written != content:
        return "Error: write verification failed — file content mismatch"
    return f"Written: {path} ({len(written)} bytes)"
