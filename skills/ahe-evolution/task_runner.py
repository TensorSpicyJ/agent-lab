"""
Task Runner — Execute research tasks and produce scored traces.

Phase 1 of the AHE evolution loop. For each task:
  1. Set up an isolated sandbox (copy harness + knowledge)
  2. Build agent from harness components (system prompt, tools, middleware)
  3. Run agent loop with middleware pipeline
  4. Record full trace (every turn, tool call, middleware action)
  5. Run mechanized scoring checks on outputs
  6. Write trace.json, score.json, and result.json
"""

import json
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import yaml

import sys
from pathlib import Path as _Path
_SKILL_DIR = _Path(__file__).resolve().parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

from shared.config_loader import load_config
from shared.sandbox import Sandbox
from shared.scoring import score_task, build_scoring_dimensions
# Tool sandbox root injection happens in run_task via _set_sandbox_root_all


# ═══════════════════════════════════════════════════════
# Tool Registry — load tools from agent.yaml
# ═══════════════════════════════════════════════════════

def _load_tool_registry(harness_dir: Path, agent_yaml: dict) -> dict[str, callable]:
    """Dynamically load tool implementations from agent.yaml registrations.
    Returns {tool_name: callable_function}.

    Tools are standalone Python files with no relative imports.
    Each module is exec'd and the target function extracted.
    """
    registry = {}

    for tool_entry in agent_yaml.get("tools", []):
        name = tool_entry["name"]
        binding = tool_entry["binding"]  # e.g. "tools.file_tools:read_file"

        module_path, func_name = binding.split(":")
        module_file = (harness_dir / f"{module_path.replace('.', '/')}.py").resolve()
        scope_key = str(module_file)

        try:
            if scope_key not in _TOOL_MODULE_SCOPES:
                code = compile(module_file.read_text(encoding="utf-8"), str(module_file), "exec")
                module_scope: dict = {}
                exec(code, module_scope)
                _TOOL_MODULE_SCOPES[scope_key] = module_scope
            else:
                module_scope = _TOOL_MODULE_SCOPES[scope_key]
            registry[name] = module_scope[func_name]
        except Exception as e:
            print(f"  [task_runner] Warning: failed to load tool '{name}' from {binding}: {e}")

    return registry


def _ensure_package(package_name: str, package_dir: Path):
    """Register a directory as a Python package in sys.modules, including parents."""
    from types import ModuleType
    import importlib.util
    parts = package_name.split(".")
    for i in range(1, len(parts) + 1):
        sub_name = ".".join(parts[:i])
        if sub_name in sys.modules:
            continue
        sub_dir = Path(*package_dir.parts[:-(len(parts)-i)]) if i < len(parts) else package_dir
        init_file = sub_dir / "__init__.py"
        if init_file.exists():
            spec = importlib.util.spec_from_file_location(sub_name, str(init_file))
            mod = importlib.util.module_from_spec(spec)
            sys.modules[sub_name] = mod
            spec.loader.exec_module(mod)
        else:
            mod = ModuleType(sub_name)
            mod.__path__ = [str(sub_dir)]
            mod.__package__ = sub_name
            sys.modules[sub_name] = mod


def _load_tool_schemas(harness_dir: Path, agent_yaml: dict) -> list[dict]:
    """Load OpenAI-format tool schemas from tool_descriptions/ YAML files."""
    schemas = []
    for tool_entry in agent_yaml.get("tools", []):
        desc_path = tool_entry.get("description_path", "")
        full_path = harness_dir / desc_path
        if full_path.exists():
            with open(full_path, encoding="utf-8") as f:
                desc = yaml.safe_load(f)
            schemas.append({
                "type": "function",
                "function": {
                    "name": desc["name"],
                    "description": desc["description"],
                    "parameters": desc["parameters"],
                },
            })
        else:
            # Minimal fallback
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool_entry["name"],
                    "description": f"Execute {tool_entry['name']}",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            })
    return schemas


# ═══════════════════════════════════════════════════════
# Middleware Pipeline
# ═══════════════════════════════════════════════════════

# Registry of loaded tool module scopes (for sandbox root injection)
_TOOL_MODULE_SCOPES: dict[str, dict] = {}

def _set_sandbox_root_all(root: Path):
    """Inject sandbox root into all loaded tool modules."""
    for mod_scope in _TOOL_MODULE_SCOPES.values():
        if "_set_sandbox_root" in mod_scope:
            mod_scope["_set_sandbox_root"](root)


def _load_middleware_pipeline(harness_dir: Path, agent_yaml: dict) -> list:
    """Load middleware instances from agent.yaml registrations.
    Middleware uses relative imports (from . import ...) so we need proper package setup."""
    import importlib
    import importlib.util

    # Register harness package chain
    _ensure_package("harness", harness_dir)
    mw_dir = harness_dir / "middleware"
    _ensure_package("harness.middleware", mw_dir)

    pipeline = []

    for mw_entry in agent_yaml.get("middlewares", []):
        import_path = mw_entry["import"]
        params = mw_entry.get("params", {})

        # e.g. "middleware.physics_thinking:PhysicsThinkingMiddleware"
        module_path, class_name = import_path.split(":")
        module_file = mw_dir / f"{module_path.split('.', 1)[1]}.py"

        try:
            if module_file.exists():
                spec = importlib.util.spec_from_file_location(
                    f"harness.{module_path}", str(module_file)
                )
                mod = importlib.util.module_from_spec(spec)
                sys.modules[f"harness.{module_path}"] = mod
                spec.loader.exec_module(mod)
                cls = getattr(mod, class_name)
                pipeline.append(cls(**params))
            else:
                print(f"  [task_runner] Warning: middleware file not found: {module_file}")
        except Exception as e:
            print(f"  [task_runner] Warning: failed to load middleware '{import_path}': {e}")

    return pipeline


# ═══════════════════════════════════════════════════════
# Agent Loop
# ═══════════════════════════════════════════════════════

def run_task(
    task_config: dict,
    harness_dir: Path,
    knowledge_dir: Path,
    llm_config: dict,
    max_turns: int = 15,
    sandbox_root: Path | None = None,
) -> dict:
    """Execute a single research task and return trace + scores.

    Returns:
        { task_id, status, turns, trace, score, started_at, finished_at }
    """
    task_id = task_config["id"]
    started_at = datetime.now(timezone.utc).isoformat()

    trace_entries = []
    score_result = None
    final_status = "UNKNOWN"

    try:
        # ── Setup sandbox ──
        with Sandbox(harness_dir, knowledge_dir, sandbox_root) as sandbox:
            sandbox_root = sandbox.root
            _set_sandbox_root_all(sandbox_root)
            workspace = sandbox_root / "workspace"

            # ── Load harness ──
            agent_yaml_path = harness_dir / "agent.yaml"
            with open(agent_yaml_path, encoding="utf-8") as f:
                agent_yaml = yaml.safe_load(f)

            # System prompt
            system_prompt_path = harness_dir / agent_yaml.get("system_prompt", "systemprompt.md")
            if system_prompt_path.exists():
                system_prompt = system_prompt_path.read_text(encoding="utf-8")
            else:
                system_prompt = "You are a research agent."

            # Replace template variables
            system_prompt = system_prompt.replace("{{ date }}", datetime.now().strftime("%Y-%m-%d"))
            system_prompt = system_prompt.replace("{{ working_directory }}", str(workspace))
            system_prompt = system_prompt.replace("{{ knowledge_root }}", str(sandbox_root / "knowledge"))

            # Tools
            tool_registry = _load_tool_registry(harness_dir, agent_yaml)
            tool_schemas = _load_tool_schemas(harness_dir, agent_yaml)
            stop_tools = set(agent_yaml.get("stop_tools", ["complete_task"]))

            # Middleware
            middleware_pipeline = _load_middleware_pipeline(harness_dir, agent_yaml)

            # ── Build task prompt ──
            skill = task_config.get("skill", "")
            description = task_config.get("description", "")
            task_input = task_config.get("input", {})
            task_prompt = f"""## Task: {task_config['name']}

{description}

### Instructions
Use the `{skill}` approach to complete this task. Load the relevant skill
from the harness skill directory if available.

### Input
```yaml
{yaml.dump(task_input, allow_unicode=True)}
```

### Expected Outputs
```yaml
{yaml.dump(task_config.get('expected_outputs', []), allow_unicode=True)}
```

Work step by step. When done, call `complete_task` with a summary.
"""

            # ── Agent loop ──
            from openai import OpenAI
            client = OpenAI(
                base_url=llm_config.get("base_url", "https://api.deepseek.com"),
                api_key=llm_config.get("api_key", ""),
            )
            model = llm_config.get("model", "deepseek-chat")

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": task_prompt},
            ]

            for turn in range(1, max_turns + 1):
                trace_entry = {"turn": turn, "llm_call": {}, "tool_executions": [], "middleware_actions": []}

                # ── before_model middleware ──
                for mw in middleware_pipeline:
                    result = mw.before_model(messages)
                    if result.modified and result.messages:
                        messages = result.messages
                        trace_entry["middleware_actions"].append({
                            "hook": "before_model",
                            "middleware": type(mw).__name__,
                            "warnings": result.warnings,
                        })

                # ── LLM call ──
                llm_resp = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    tools=tool_schemas or None,
                    temperature=0.2,
                )
                msg = llm_resp.choices[0].message
                trace_entry["llm_call"] = {
                    "content": msg.content[:500] if msg.content else None,
                    "tool_calls": [
                        {"name": tc.function.name, "arguments": tc.function.arguments}
                        for tc in (msg.tool_calls or [])
                    ],
                    "finish_reason": llm_resp.choices[0].finish_reason,
                }

                # ── after_model middleware ──
                for mw in middleware_pipeline:
                    result = mw.after_model(msg.content or "")
                    if result.warnings:
                        trace_entry["middleware_actions"].append({
                            "hook": "after_model",
                            "middleware": type(mw).__name__,
                            "warnings": result.warnings,
                        })

                # ── No tool calls → agent done ──
                if not msg.tool_calls:
                    content = msg.content or ""
                    if "DONE" in content:
                        final_status = "DONE"
                    elif "BLOCKED" in content:
                        final_status = "BLOCKED"
                    else:
                        final_status = "FINISHED"
                    messages.append({"role": "assistant", "content": content})
                    trace_entries.append(trace_entry)
                    break

                # ── Execute tools ──
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                        }
                        for tc in msg.tool_calls
                    ],
                })

                for tc in msg.tool_calls:
                    tool_name = tc.function.name
                    tool_args = json.loads(tc.function.arguments)

                    # before_tool middleware
                    for mw in middleware_pipeline:
                        result = mw.before_tool(tool_name, tool_args)
                        if result.modified and result.tool_args:
                            tool_args = result.tool_args

                    # Execute
                    tool_fn = tool_registry.get(tool_name)
                    if tool_fn:
                        try:
                            import inspect
                            sig = inspect.signature(tool_fn)
                            if len(sig.parameters) == 1:
                                tool_result = tool_fn(tool_args)
                            else:
                                tool_result = tool_fn(**tool_args)
                        except Exception as tool_err:
                            tool_result = f"Error: {tool_err}"
                    else:
                        tool_result = f"Unknown tool: {tool_name}"

                    # after_tool middleware
                    tool_warnings = []
                    for mw in middleware_pipeline:
                        result = mw.after_tool(tool_name, str(tool_result))
                        if result.warnings:
                            tool_warnings.extend(result.warnings)

                    trace_entry["tool_executions"].append({
                        "name": tool_name,
                        "args": tool_args,
                        "result": str(tool_result)[:500],
                        "warnings": tool_warnings,
                    })

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": str(tool_result),
                    })

                    # Stop tool check
                    if tool_name in stop_tools:
                        final_status = "DONE"
                        trace_entries.append(trace_entry)
                        break

                trace_entries.append(trace_entry)
                if final_status == "DONE":
                    break

            else:
                final_status = "MAX_TURNS"

            # ── Scoring ──
            dimensions = build_scoring_dimensions(task_config)
            score_result = score_task(workspace, dimensions)

    except Exception as exc:
        final_status = "ERROR"
        trace_entries.append({
            "turn": -1,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        })

    finished_at = datetime.now(timezone.utc).isoformat()

    return {
        "task_id": task_id,
        "status": final_status,
        "turns": len(trace_entries),
        "trace": trace_entries,
        "score": score_result,
        "started_at": started_at,
        "finished_at": finished_at,
    }


# ═══════════════════════════════════════════════════════
# Batch Runner
# ═══════════════════════════════════════════════════════

def run_all_tasks(
    config: dict,
    tasks: list[dict],
    harness_dir: Path,
    knowledge_dir: Path,
    results_dir: Path,
    k: int = 1,
) -> list[dict]:
    """Run all tasks (with k rollouts each) and save results.

    Returns list of per-task results.
    """
    llm_config = config["llm"]
    max_turns = config.get("evaluation", {}).get("max_turns", 15)
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)

    all_results = []

    for task_config in tasks:
        task_id = task_config["id"]
        task_results_dir = results_dir / task_id
        task_results_dir.mkdir(parents=True, exist_ok=True)

        # Run k rollouts
        best_score = -1
        best_result = None
        for rollout in range(1, k + 1):
            print(f"  [{task_id}] Rollout {rollout}/{k}")
            result = run_task(
                task_config=task_config,
                harness_dir=harness_dir,
                knowledge_dir=knowledge_dir,
                llm_config=llm_config,
                max_turns=max_turns,
            )

            # Save rollout trace
            rollout_dir = task_results_dir / f"rollout_{rollout}"
            rollout_dir.mkdir(parents=True, exist_ok=True)
            with open(rollout_dir / "trace.json", "w", encoding="utf-8") as f:
                json.dump(result["trace"], f, ensure_ascii=False, indent=2)
            if result["score"]:
                with open(rollout_dir / "score.json", "w", encoding="utf-8") as f:
                    json.dump(result["score"], f, ensure_ascii=False, indent=2)

            score = result["score"]["overall_score"] if result["score"] else 0.0
            if score > best_score:
                best_score = score
                best_result = result

        # Write best-rollout result
        if best_result:
            with open(task_results_dir / "result.json", "w", encoding="utf-8") as f:
                json.dump({
                    "task_id": task_id,
                    "status": best_result["status"],
                    "turns": best_result["turns"],
                    "score": best_result["score"],
                    "started_at": best_result["started_at"],
                    "finished_at": best_result["finished_at"],
                }, f, ensure_ascii=False, indent=2)

        all_results.append(best_result)

    # Write aggregate results
    aggregate = _aggregate_results(all_results, tasks)
    with open(results_dir / "result.json", "w", encoding="utf-8") as f:
        json.dump(aggregate, f, ensure_ascii=False, indent=2)

    return all_results


def _aggregate_results(results: list[dict], tasks: list[dict]) -> dict:
    """Compute aggregate quality metrics across all tasks."""
    task_scores = {}
    for r in results:
        if r and r.get("score"):
            task_scores[r["task_id"]] = r["score"]["overall_score"]

    scores = list(task_scores.values())
    avg_score = sum(scores) / len(scores) if scores else 0.0
    passed = sum(1 for s in scores if s >= 0.5)

    return {
        "overall_score": round(avg_score, 4),
        "tasks_passed": passed,
        "tasks_total": len(tasks),
        "per_task": task_scores,
        "aggregated_at": datetime.now(timezone.utc).isoformat(),
    }
