import sys
from pathlib import Path

from .lean_verify_lib import run_verifier_for_task


def _task_dir(name: str) -> Path:
    return Path(__file__).resolve().parents[1] / "tasks" / name


def verify_visviva() -> int:
    return run_verifier_for_task(_task_dir("visviva-speedcircular-sq-proof"), Path(sys.argv[1]))


def verify_eulerlagrange() -> int:
    return run_verifier_for_task(_task_dir("eulerlagrange-zero-proof"), Path(sys.argv[1]))


def verify_idealgas() -> int:
    return run_verifier_for_task(_task_dir("idealgas-adiabatic-product-proof"), Path(sys.argv[1]))
