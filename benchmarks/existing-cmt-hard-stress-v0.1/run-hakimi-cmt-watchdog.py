import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_ON_FLAGS = [
    "KIMI_CODE_EXPERIMENTAL_PHYSICS_MEMORY",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_LEDGER",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_ACTION",
    "KIMI_CODE_EXPERIMENTAL_DOMAIN_PROFILE",
    "KIMI_CODE_EXPERIMENTAL_WORKFLOW_RECIPE",
    "KIMI_CODE_EXPERIMENTAL_RESEARCH_HARNESS",
    "KIMI_CODE_EXPERIMENTAL_GOAL_COMMAND",
]

ALL_FLAG_NAMES = DEFAULT_ON_FLAGS + [
    "KIMI_CODE_EXPERIMENTAL_MICRO_COMPACTION",
    "KIMI_CODE_EXPERIMENTAL_BACKGROUND_ASK",
    "KIMI_CODE_EXPERIMENTAL_FLAG",
]


def now_iso():
    return datetime.now().astimezone().isoformat()


def timestamp():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def safe_name(text):
    return re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_")


def read_text_best_effort(path):
    path = Path(path)
    if not path.exists():
        return ""
    raw = path.read_bytes()
    if not raw:
        return ""
    for enc in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def problem_block(full_prompt, problem_number):
    next_number = problem_number + 1
    pattern = rf"(?s)(### {problem_number}\..*?)(?=### {next_number}\.|$)"
    match = re.search(pattern, full_prompt)
    if not match:
        raise RuntimeError(f"Problem block not found: {problem_number}")
    return match.group(1).strip()


def parse_problem_list(value, total):
    if not value:
        return list(range(1, total + 1))
    items = []
    for part in re.split(r"[,\s]+", value.strip()):
        if not part:
            continue
        if "-" in part:
            left, right = part.split("-", 1)
            items.extend(range(int(left), int(right) + 1))
        else:
            items.append(int(part))
    for item in items:
        if item < 1 or item > total:
            raise ValueError(f"Problem number out of range: {item}")
    return items


def parse_jsonish(candidate):
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        repaired = re.sub(r"(?<!\\)\\(?!(?:[\"\\/bfnrt]|u[0-9a-fA-F]{4}))", r"\\\\", candidate)
        return json.loads(repaired)


def find_fenced_json(text):
    for match in re.finditer(r"(?is)```(?:json)?\s*(\{.*?\})\s*```", text):
        candidate = match.group(1)
        try:
            parse_jsonish(candidate)
            return candidate
        except json.JSONDecodeError:
            continue
    return None


def find_balanced_json(text):
    starts = [i for i, ch in enumerate(text) if ch == "{"]
    for start in starts:
        depth = 0
        in_string = False
        escaped = False
        for idx in range(start, len(text)):
            ch = text[idx]
            if in_string:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == '"':
                    in_string = False
                continue
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = text[start : idx + 1]
                    try:
                        parse_jsonish(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        break
    return None


def extract_json_object(text):
    return find_fenced_json(text) or find_balanced_json(text)


def kill_tree(pid):
    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        try:
            os.kill(pid, 15)
        except ProcessLookupError:
            return
        time.sleep(1)
        try:
            os.kill(pid, 9)
        except ProcessLookupError:
            pass


def file_size(path):
    try:
        return Path(path).stat().st_size
    except FileNotFoundError:
        return 0


def mode_env(base_env, home_dir, flags_off):
    env = dict(base_env)
    env["HAKIMI_HOME"] = str(home_dir)
    env.pop("KIMI_CODE_HOME", None)
    for name in ALL_FLAG_NAMES:
        env.pop(name, None)
    if flags_off:
        for name in DEFAULT_ON_FLAGS:
            env[name] = "0"
        env["KIMI_CODE_EXPERIMENTAL_MICRO_COMPACTION"] = "0"
        env["KIMI_CODE_EXPERIMENTAL_BACKGROUND_ASK"] = "0"
        env["KIMI_CODE_EXPERIMENTAL_FLAG"] = "0"
    return env


def prepare_home(temp_root, mode_name, source_config):
    home_dir = temp_root / f"hakimi-home-{mode_name}"
    home_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_config, home_dir / "config.toml")
    return home_dir


def read_flag_lines(home_dir):
    log_path = Path(home_dir) / "logs" / "kimi-code.log"
    if not log_path.exists():
        return []
    return [
        line
        for line in read_text_best_effort(log_path).splitlines()
        if "experimental flags enabled" in line
    ]


def invoke_with_watchdog(command, cwd, env, stdout_path, stderr_path, idle_timeout_s, max_runtime_s, poll_s, live_cb):
    stdout_path = Path(stdout_path)
    stderr_path = Path(stderr_path)
    stdout_path.parent.mkdir(parents=True, exist_ok=True)
    stderr_path.parent.mkdir(parents=True, exist_ok=True)
    started = time.monotonic()
    last_growth = started
    last_bytes = 0
    with stdout_path.open("wb") as out_f, stderr_path.open("wb") as err_f:
        proc = subprocess.Popen(command, cwd=str(cwd), env=env, stdout=out_f, stderr=err_f)
        status = "running"
        exit_code = None
        while True:
            time.sleep(poll_s)
            now = time.monotonic()
            total_bytes = file_size(stdout_path) + file_size(stderr_path)
            if total_bytes > last_bytes:
                last_bytes = total_bytes
                last_growth = now
            runtime_s = now - started
            idle_s = now - last_growth
            live_cb(status, runtime_s, idle_s, file_size(stdout_path), file_size(stderr_path))
            rc = proc.poll()
            if rc is not None:
                status = "completed"
                exit_code = rc
                break
            if max_runtime_s > 0 and runtime_s >= max_runtime_s:
                status = "max_runtime_timeout"
                exit_code = -2
                kill_tree(proc.pid)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
                break
            if idle_s >= idle_timeout_s:
                status = "idle_timeout"
                exit_code = -1
                kill_tree(proc.pid)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    pass
                break
    finished = time.monotonic()
    return {
        "status": status,
        "exit_code": exit_code,
        "runtime_seconds": round(finished - started, 3),
        "stdout_bytes": file_size(stdout_path),
        "stderr_bytes": file_size(stderr_path),
    }


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-id", default="cmt-hard-research-50")
    parser.add_argument("--problem-list", default="")
    parser.add_argument("--model", default="deepseek/deepseek-v4-pro")
    parser.add_argument("--modes", default="default_on,all_default_on_flags_off")
    parser.add_argument("--idle-timeout-minutes", type=float, default=4)
    parser.add_argument("--max-runtime-minutes", type=float, default=6)
    parser.add_argument("--poll-seconds", type=float, default=5)
    parser.add_argument("--run-label", default="watchdog")
    parser.add_argument("--node", default="node")
    parser.add_argument("--hakimi-main", default=r"D:\Playground\Hakimi\apps\kimi-code\dist\main.mjs")
    args = parser.parse_args()

    benchmark_root = Path(__file__).resolve().parent
    task_root = benchmark_root / "tasks" / args.task_id
    prompt_path = task_root / "prompt.md"
    verifier_path = task_root / "verify.py"
    gold_path = task_root / "private" / "gold.json"
    source_config = Path.home() / ".hakimi" / "config.toml"
    hakimi_main = Path(args.hakimi_main)
    for path in [prompt_path, verifier_path, gold_path, source_config, hakimi_main]:
        if not path.exists():
            raise FileNotFoundError(path)

    gold = load_json(gold_path)
    fields = [item["field"] for item in gold["checks"]]
    full_prompt = prompt_path.read_text(encoding="utf-8")
    problem_numbers = parse_problem_list(args.problem_list, len(fields))

    run_id = f"{timestamp()}__hakimi013_deepseek_watchdog__{safe_name(args.task_id)}__{safe_name(args.run_label)}"
    run_root = benchmark_root / "runs" / run_id
    output_dir = run_root / "outputs"
    score_dir = run_root / "scores"
    logs_dir = run_root / "logs"
    temp_root = Path(tempfile.gettempdir()) / f"agent-lab-{run_id}"
    for path in [output_dir, score_dir, logs_dir, temp_root]:
        path.mkdir(parents=True, exist_ok=True)

    started_at = now_iso()
    modes = []
    for mode_name in [m.strip() for m in args.modes.split(",") if m.strip()]:
        if mode_name == "default_on":
            modes.append({"name": mode_name, "flags_off": False})
        elif mode_name in {"all_default_on_flags_off", "flags_off"}:
            modes.append({"name": "all_default_on_flags_off", "flags_off": True})
        else:
            raise ValueError(f"Unknown mode: {mode_name}")

    mode_homes = {}
    for mode in modes:
        mode_homes[mode["name"]] = prepare_home(temp_root, mode["name"], source_config)

    live_path = run_root / "live-status.json"
    partial_path = run_root / "run-metadata.partial.json"
    base_env = os.environ.copy()
    mode_results = []

    def write_partial(current_mode=None, item_runs=None):
        write_json(
            partial_path,
            {
                "benchmark_id": "existing-cmt-hard-stress-v0.1",
                "task_id": args.task_id,
                "run_id": run_id,
                "current_mode": current_mode,
                "model_alias": args.model,
                "problem_numbers": problem_numbers,
                "temp_home_root": str(temp_root),
                "modes": mode_results,
                "current_item_runs": item_runs or [],
                "updated_at": now_iso(),
            },
        )

    for mode in modes:
        mode_name = mode["name"]
        home_dir = mode_homes[mode_name]
        env = mode_env(base_env, home_dir, mode["flags_off"])
        mode_output = output_dir / f"{args.task_id}.{mode_name}.json"
        mode_score = score_dir / f"{args.task_id}.{mode_name}.full-score.json"
        mode_summary = score_dir / f"{args.task_id}.{mode_name}.summary.json"
        mode_merged = {}
        item_runs = []

        # Smoke commands also capture flag logs for the mode.
        for smoke_name, smoke_args in {
            "provider": ["provider", "list"],
            "version": ["--version"],
        }.items():
            stdout_path = logs_dir / f"{mode_name}.{smoke_name}.stdout.txt"
            stderr_path = logs_dir / f"{mode_name}.{smoke_name}.stderr.txt"
            command = [args.node, str(hakimi_main)] + smoke_args
            invoke_with_watchdog(
                command,
                benchmark_root,
                env,
                stdout_path,
                stderr_path,
                120,
                120,
                2,
                lambda *_: None,
            )

        for problem_number in problem_numbers:
            field = fields[problem_number - 1]
            prompt_file = logs_dir / f"{mode_name}.item-{problem_number:02d}-{field}.prompt.md"
            stdout_file = logs_dir / f"{mode_name}.item-{problem_number:02d}-{field}.stdout.txt"
            stderr_file = logs_dir / f"{mode_name}.item-{problem_number:02d}-{field}.stderr.txt"
            item_cwd = temp_root / f"{mode_name}-item-{problem_number:02d}"
            item_cwd.mkdir(parents=True, exist_ok=True)
            item_prompt = f"""# {args.task_id} Item {problem_number}

Return exactly one JSON object and no explanation.

Use exactly this key:

- `{field}`

For multiple-answer questions, return a semicolon-separated lowercase choice set such as "a;b;d".
For symbolic answers, use compact LaTeX-like strings.
For numeric vectors, return a JSON array of numbers.

{problem_block(full_prompt, problem_number)}
"""
            prompt_file.write_text(item_prompt, encoding="utf-8")
            shutil.copy2(prompt_file, item_cwd / "prompt.md")
            prompt_text = """Read prompt.md in the current directory and complete the benchmark item exactly as written.

Important:
- Do not browse the web or use search.
- Do not ask a follow-up question.
- Output exactly one JSON object and no explanation.
"""
            command = [
                args.node,
                str(hakimi_main),
                "-m",
                args.model,
                "-p",
                prompt_text,
                "--output-format",
                "text",
            ]

            def live_cb(status, runtime_s, idle_s, stdout_bytes, stderr_bytes):
                write_json(
                    live_path,
                    {
                        "benchmark_id": "existing-cmt-hard-stress-v0.1",
                        "task_id": args.task_id,
                        "run_id": run_id,
                        "mode": mode_name,
                        "problem_number": problem_number,
                        "field": field,
                        "status": status,
                        "runtime_seconds": round(runtime_s, 3),
                        "idle_seconds": round(idle_s, 3),
                        "stdout_bytes": stdout_bytes,
                        "stderr_bytes": stderr_bytes,
                        "updated_at": now_iso(),
                    },
                )

            result = invoke_with_watchdog(
                command,
                item_cwd,
                env,
                stdout_file,
                stderr_file,
                args.idle_timeout_minutes * 60,
                args.max_runtime_minutes * 60,
                args.poll_seconds,
                live_cb,
            )
            stdout_text = read_text_best_effort(stdout_file)
            json_text = extract_json_object(stdout_text)
            captured = False
            if json_text:
                try:
                    parsed = parse_jsonish(json_text)
                    if field in parsed:
                        mode_merged[field] = parsed[field]
                        captured = True
                except json.JSONDecodeError:
                    pass
            item_record = {
                "mode": mode_name,
                "field": field,
                "problem_number": problem_number,
                "status": result["status"],
                "exit_code": result["exit_code"],
                "runtime_seconds": result["runtime_seconds"],
                "stdout_bytes": result["stdout_bytes"],
                "stderr_bytes": result["stderr_bytes"],
                "captured_json": captured,
                "prompt": str(prompt_file),
                "stdout": str(stdout_file),
                "stderr": str(stderr_file),
            }
            item_runs.append(item_record)
            write_partial(mode_name, item_runs)

        mode_output.write_text(json.dumps(mode_merged, ensure_ascii=False, indent=2), encoding="utf-8")
        verifier_env = dict(os.environ)
        verifier_env["PYTHONIOENCODING"] = "utf-8"
        score_proc = subprocess.run(
            [sys.executable, str(verifier_path), str(mode_output)],
            cwd=str(task_root),
            env=verifier_env,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        mode_score.write_text(score_proc.stdout, encoding="utf-8")
        (logs_dir / f"{mode_name}.scorer.stderr.txt").write_text(score_proc.stderr, encoding="utf-8")
        score = json.loads(score_proc.stdout)
        slice_fields = {fields[number - 1] for number in problem_numbers}
        slice_checks = [item for item in score["checks"] if item["field"] in slice_fields]
        slice_passed = sum(1 for item in slice_checks if item.get("passed"))
        mode_summary_obj = {
            "benchmark_id": "existing-cmt-hard-stress-v0.1",
            "task_id": args.task_id,
            "run_id": run_id,
            "mode": mode_name,
            "model_alias": args.model,
            "problem_numbers": problem_numbers,
            "passed": slice_passed,
            "total": len(slice_checks),
            "hard_score": (slice_passed / len(slice_checks)) if slice_checks else None,
            "output": str(mode_output),
            "full_score": str(mode_score),
            "item_runs": item_runs,
            "experimental_flag_log_lines": read_flag_lines(home_dir),
            "scorer_exit_code": score_proc.returncode,
        }
        write_json(mode_summary, mode_summary_obj)
        mode_results.append(
            {
                "mode": mode_name,
                "passed": slice_passed,
                "total": len(slice_checks),
                "hard_score": mode_summary_obj["hard_score"],
                "output": str(mode_output),
                "full_score": str(mode_score),
                "summary": str(mode_summary),
                "item_run_count": len(item_runs),
                "experimental_flag_log_lines": read_flag_lines(home_dir),
            }
        )
        write_partial()

    metadata = {
        "benchmark_id": "existing-cmt-hard-stress-v0.1",
        "task_id": args.task_id,
        "run_id": run_id,
        "agent": "hakimi013_deepseek_watchdog",
        "model_alias": args.model,
        "command": "node main.mjs -m <model> -p <single problem prompt> --output-format text",
        "started_at": started_at,
        "finished_at": now_iso(),
        "idle_timeout_minutes": args.idle_timeout_minutes,
        "max_runtime_minutes": args.max_runtime_minutes,
        "poll_seconds": args.poll_seconds,
        "problem_numbers": problem_numbers,
        "source_config": "~/.hakimi/config.toml copied into isolated temp homes; API keys are not stored in this run directory.",
        "temp_home_root": str(temp_root),
        "local_leakage_boundary": "Each item temp cwd contains only prompt.md. Gold, verifier, source rows, and prior outputs are not mounted in cwd.",
        "modes": mode_results,
    }
    write_json(run_root / "run-metadata.json", metadata)
    print(f"Run directory: {run_root}")
    print(f"Metadata: {run_root / 'run-metadata.json'}")


if __name__ == "__main__":
    run()
