import importlib.util
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE_VERIFY = HERE.parent / "open-physics-diverse-mini-8" / "verify.py"

spec = importlib.util.spec_from_file_location("open_physics_diverse_verify", BASE_VERIFY)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.GOLD_PATH = HERE / "private" / "gold.json"

raise SystemExit(module.main(sys.argv))
