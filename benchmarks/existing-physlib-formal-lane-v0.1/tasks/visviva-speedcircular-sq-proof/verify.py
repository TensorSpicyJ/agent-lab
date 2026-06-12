from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools import verify_visviva  # type: ignore


if __name__ == "__main__":
    raise SystemExit(verify_visviva())
