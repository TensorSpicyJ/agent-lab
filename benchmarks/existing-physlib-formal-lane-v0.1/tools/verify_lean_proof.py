import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.lean_verify_lib import run_verifier_for_task  # type: ignore


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: python verify_lean_proof.py <task_dir> <answer.md>")
        return 2
    task_dir = Path(sys.argv[1]).resolve()
    answer_path = Path(sys.argv[2]).resolve()
    return run_verifier_for_task(task_dir, answer_path)


if __name__ == "__main__":
    raise SystemExit(main())
