"""Shell execution tool with safety checks."""

import subprocess
from pathlib import Path

# Injected by task_runner
_SANDBOX_ROOT: Path | None = None


def _set_sandbox_root(root: Path):
    global _SANDBOX_ROOT
    _SANDBOX_ROOT = root


_DANGEROUS_PATTERNS = [
    "rm -rf /", "mkfs.", "dd if=", "> /dev/sda",
    "format c:", "del /f /s",
    "shutdown", "reboot", "halt",
]


def run_shell(command: str, timeout: int = 30) -> str:
    """Execute a shell command."""
    cmd_lower = command.lower()
    for pattern in _DANGEROUS_PATTERNS:
        if pattern.lower() in cmd_lower:
            return f"DENIED: dangerous command pattern '{pattern}'"

    cwd = str(_SANDBOX_ROOT) if _SANDBOX_ROOT else None
    try:
        result = subprocess.run(
            command, shell=True, capture_output=True, text=True,
            timeout=timeout, cwd=cwd,
        )
        output = result.stdout
        if result.stderr:
            output += "\n[stderr]\n" + result.stderr
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return f"Error: command timed out after {timeout}s"
    except Exception as e:
        return f"Error executing shell command: {e}"
