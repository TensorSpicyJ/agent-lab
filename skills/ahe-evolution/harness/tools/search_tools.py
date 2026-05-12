"""Grep and glob search tools."""

import re
from pathlib import Path

# Injected by task_runner
_SANDBOX_ROOT: Path | None = None


def _set_sandbox_root(root: Path):
    global _SANDBOX_ROOT
    _SANDBOX_ROOT = root


def grep(pattern: str, path: str = ".", glob_filter: str | None = None) -> str:
    """Search file contents by regex pattern."""
    if _SANDBOX_ROOT is None:
        raise RuntimeError("Sandbox root not set")

    search_dir = _SANDBOX_ROOT / path
    if not search_dir.exists():
        return f"Error: path not found: {path}"

    try:
        compiled = re.compile(pattern)
    except re.error as e:
        return f"Error: invalid regex pattern: {e}"

    pattern_obj = glob_filter or "*"
    files = list(search_dir.rglob(pattern_obj))
    files = [f for f in files if f.is_file() and f.suffix not in
             (".pyc", ".o", ".exe", ".dll", ".so", ".wasm", ".bin", ".zip", ".gz")]

    results = []
    for filepath in files[:500]:
        try:
            for line_no, line in enumerate(filepath.read_text(encoding="utf-8", errors="replace").split("\n"), 1):
                if compiled.search(line):
                    rel_path = filepath.relative_to(_SANDBOX_ROOT)
                    results.append(f"{rel_path}:{line_no}: {line.rstrip()[:200]}")
        except Exception:
            continue

    if not results:
        return f"No matches for pattern '{pattern}'"
    return "\n".join(results[:200])


def glob_search(pattern: str, path: str = ".") -> str:
    """Find files by glob pattern relative to sandbox root."""
    if _SANDBOX_ROOT is None:
        raise RuntimeError("Sandbox root not set")

    search_dir = _SANDBOX_ROOT / path
    if not search_dir.exists():
        return f"Error: path not found: {path}"

    matches = list(search_dir.glob(pattern))
    if not matches:
        return f"No files matching '{pattern}'"

    matches.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    lines = []
    for m in matches[:100]:
        rel = m.relative_to(_SANDBOX_ROOT)
        tag = "/" if m.is_dir() else ""
        lines.append(f"{rel}{tag}")
    return "\n".join(lines)
