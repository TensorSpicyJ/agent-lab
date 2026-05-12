"""Session control tool — signals task completion."""


def complete_task(summary: str) -> str:
    """Signal that the task is complete. Provide a summary of what was done.
    This is the ONLY way to end a task — the harness checks for this call."""
    return f"DONE. Task completed: {summary}"
