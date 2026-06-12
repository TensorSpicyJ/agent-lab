import json
import os
import re
import subprocess
import tempfile
from pathlib import Path


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def extract_answer(text: str) -> str:
    matches = re.findall(r"```(?:lean)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    if matches:
        return matches[-1].strip()
    return text.strip()


def indent_block(text: str, spaces: int = 2) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else "" for line in text.splitlines())


def run_verifier_for_task(task_dir: Path, answer_path: Path) -> int:
    config = json.loads((task_dir / "task.json").read_text(encoding="utf-8"))
    template = (task_dir / "private" / "template.lean").read_text(encoding="utf-8")
    answer = extract_answer(read_text_flexible(answer_path))
    lean_code = template.replace("{{PROOF}}", indent_block(answer))

    repo_path = Path(os.environ.get("PHYSLIB_REPO", config["repo_default"]))
    timeout_seconds = int(config.get("timeout_seconds", 240))
    benchmark_id = config["benchmark_id"]
    task_id = config["task_id"]

    with tempfile.TemporaryDirectory(prefix="physlib-bench-") as tmp:
        lean_path = Path(tmp) / "BenchTask.lean"
        lean_path.write_text(lean_code, encoding="utf-8")
        env = os.environ.copy()
        lean_path_entries = [str(repo_path)]
        existing_lean_path = env.get("LEAN_PATH", "")
        if existing_lean_path:
            lean_path_entries.append(existing_lean_path)
        env["LEAN_PATH"] = os.pathsep.join(lean_path_entries)
        try:
            completed = subprocess.run(
                ["lake", "env", "lean", str(lean_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            print(json.dumps({
                "benchmark_id": benchmark_id,
                "task_id": task_id,
                "status": "environment_timeout",
                "hard_score": None,
                "passed": False,
                "error": "lean_verification_timeout",
                "stdout_tail": (exc.stdout or "")[-2000:],
                "stderr_tail": (exc.stderr or "")[-2000:],
                "repo_path": str(repo_path),
            }, ensure_ascii=False, indent=2))
            return 1

    stdout = completed.stdout[-4000:]
    stderr = completed.stderr[-4000:]
    diagnostic_text = "\n".join(part for part in (completed.stdout, completed.stderr) if part)
    if completed.returncode == 0:
        print(json.dumps({
            "benchmark_id": benchmark_id,
            "task_id": task_id,
            "status": "verified",
            "hard_score": 1.0,
            "passed": True,
            "repo_path": str(repo_path),
        }, ensure_ascii=False, indent=2))
        return 0

    env_error = None
    if "external command 'git' exited with code 128" in diagnostic_text:
        env_error = "git_dependency_failure"
    elif "URL has changed" in diagnostic_text:
        env_error = "stale_dependency_remote"
    elif "object file" in diagnostic_text and "does not exist" in diagnostic_text:
        env_error = "module_prebuild_required"
    elif "unknown module prefix" in diagnostic_text:
        env_error = "module_search_path_failure"

    print(json.dumps({
        "benchmark_id": benchmark_id,
        "task_id": task_id,
        "status": "environment_error" if env_error else "failed",
        "hard_score": None if env_error else 0.0,
        "passed": False,
        "error": env_error or "lean_check_failed",
        "stdout_tail": stdout,
        "stderr_tail": stderr,
        "repo_path": str(repo_path),
    }, ensure_ascii=False, indent=2))
    return 1
