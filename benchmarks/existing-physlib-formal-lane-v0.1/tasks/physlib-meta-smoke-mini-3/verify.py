import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path


BENCHMARK_ID = "existing-physlib-formal-lane-v0.1"
TASK_ID = "physlib-meta-smoke-mini-3"
REPO_DEFAULT = Path("C:/Users/TaiS/AppData/Local/Temp/physlean-inspect")
TIMEOUT_SECONDS = 120

TEMPLATES = {
    "informal_definition_deps": """import Physlib.Meta.Informal.Basic

example (deps : List Lean.Name) (tag : String) :
    (⟨deps, tag⟩ : InformalDefinition).deps = deps := by
{{PROOF}}
""",
    "informal_lemma_tag": """import Physlib.Meta.Informal.Basic

example (deps : List Lean.Name) (tag : String) :
    (⟨deps, tag⟩ : InformalLemma).tag = tag := by
{{PROOF}}
""",
    "todo_info_line": """import Physlib.Meta.TODO.Basic

open Physlib

example (content tag : String) (fileName : Lean.Name) (line : Nat) :
    ({ content := content, fileName := fileName, line := line, tag := tag } : todoInfo).line = line := by
{{PROOF}}
""",
}


def read_text_flexible(path: Path) -> str:
    raw = path.read_bytes()
    for encoding in ("utf-8-sig", "utf-16", "utf-16-le", "utf-16-be"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    return raw.decode("utf-8", errors="replace")


def extract_json_object(text: str) -> dict:
    fenced = re.findall(r"```(?:json)?\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
    candidates = fenced + [text]
    for candidate in candidates:
        start = candidate.find("{")
        end = candidate.rfind("}")
        if start == -1 or end == -1 or end <= start:
            continue
        try:
            data = json.loads(candidate[start : end + 1])
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict):
            return data
    raise ValueError("could not parse JSON object from answer")


def indent_block(text: str, spaces: int = 2) -> str:
    prefix = " " * spaces
    return "\n".join(prefix + line if line.strip() else "" for line in text.splitlines())


def classify_env_error(stdout: str, stderr: str) -> str | None:
    diagnostic_text = "\n".join(part for part in (stdout, stderr) if part)
    if "external command 'git' exited with code 128" in diagnostic_text:
        return "git_dependency_failure"
    if "URL has changed" in diagnostic_text:
        return "stale_dependency_remote"
    if "object file" in diagnostic_text and "does not exist" in diagnostic_text:
        return "module_prebuild_required"
    if "unknown module prefix" in diagnostic_text:
        return "module_search_path_failure"
    return None


def run_lean(repo_path: Path, key: str, proof: str) -> dict:
    lean_code = TEMPLATES[key].replace("{{PROOF}}", indent_block(proof))
    with tempfile.TemporaryDirectory(prefix="physlib-smoke-") as tmp:
        lean_path = Path(tmp) / f"{key}.lean"
        lean_path.write_text(lean_code, encoding="utf-8")
        env = os.environ.copy()
        entries = [str(repo_path)]
        if env.get("LEAN_PATH"):
            entries.append(env["LEAN_PATH"])
        env["LEAN_PATH"] = os.pathsep.join(entries)
        try:
            completed = subprocess.run(
                ["lake", "env", "lean", str(lean_path)],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=TIMEOUT_SECONDS,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            return {
                "id": key,
                "passed": False,
                "error": "lean_verification_timeout",
                "environment_error": True,
                "stdout_tail": (exc.stdout or "")[-2000:],
                "stderr_tail": (exc.stderr or "")[-2000:],
            }
    stdout = completed.stdout[-2000:]
    stderr = completed.stderr[-2000:]
    env_error = classify_env_error(completed.stdout, completed.stderr)
    return {
        "id": key,
        "passed": completed.returncode == 0,
        "error": None if completed.returncode == 0 else (env_error or "lean_check_failed"),
        "environment_error": env_error is not None,
        "stdout_tail": stdout,
        "stderr_tail": stderr,
    }


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python verify.py <answer.md>")
        return 2

    answer_path = Path(sys.argv[1]).resolve()
    repo_path = Path(os.environ.get("PHYSLIB_REPO", str(REPO_DEFAULT))).resolve()
    try:
        answer = extract_json_object(read_text_flexible(answer_path))
    except Exception as exc:
        print(json.dumps({
            "benchmark_id": BENCHMARK_ID,
            "task_id": TASK_ID,
            "status": "failed",
            "hard_score": 0.0,
            "passed": 0,
            "total": len(TEMPLATES),
            "error": f"answer_parse_error: {exc}",
        }, ensure_ascii=False, indent=2))
        return 1

    results = []
    for key in TEMPLATES:
        proof = answer.get(key)
        if not isinstance(proof, str) or not proof.strip():
            results.append({
                "id": key,
                "passed": False,
                "error": "missing_or_empty_proof_body",
                "environment_error": False,
                "stdout_tail": "",
                "stderr_tail": "",
            })
            continue
        results.append(run_lean(repo_path, key, proof.strip()))

    passed = sum(1 for item in results if item["passed"])
    total = len(results)
    env_errors = [item["error"] for item in results if item.get("environment_error")]
    status = "verified" if passed == total else ("environment_error" if env_errors else "failed")
    score = None if env_errors else round(passed / total, 4)
    payload = {
        "benchmark_id": BENCHMARK_ID,
        "task_id": TASK_ID,
        "status": status,
        "hard_score": score,
        "passed": passed,
        "total": total,
        "results": results,
        "repo_path": str(repo_path),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
