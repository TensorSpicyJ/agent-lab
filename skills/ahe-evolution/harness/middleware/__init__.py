"""
AHE Evolution Middleware — pluggable hooks for the research agent loop.

Middleware hooks into the agent execution pipeline:
    before_model(msgs) -> msgs          # Inject prompts before LLM call
    after_model(response) -> response   # Post-process LLM output
    before_tool(name, args) -> args     # Validate tool arguments
    after_tool(name, result) -> result  # Check tool outputs

Each middleware returns HookResult:
    .no_changes()            — pass through unchanged
    .with_modifications(...) — mutate the pipeline state
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class HookResult:
    """Result of a middleware hook invocation."""
    modified: bool = False
    messages: list[dict] | None = None
    tool_args: dict | None = None
    tool_output: str | None = None
    warnings: list[str] = field(default_factory=list)

    @classmethod
    def no_changes(cls) -> "HookResult":
        return cls(modified=False)

    @classmethod
    def with_messages(cls, messages: list[dict], warnings: list[str] | None = None) -> "HookResult":
        return cls(modified=True, messages=messages, warnings=warnings or [])

    @classmethod
    def with_tool_output(cls, output: str, warnings: list[str] | None = None) -> "HookResult":
        return cls(modified=True, tool_output=output, warnings=warnings or [])


class Middleware:
    """Base middleware with no-op hooks. Override the hooks you need."""

    def before_model(self, messages: list[dict]) -> HookResult:
        return HookResult.no_changes()

    def after_model(self, response: str) -> HookResult:
        return HookResult.no_changes()

    def before_tool(self, tool_name: str, tool_args: dict) -> HookResult:
        return HookResult.no_changes()

    def after_tool(self, tool_name: str, tool_output: str) -> HookResult:
        return HookResult.no_changes()
