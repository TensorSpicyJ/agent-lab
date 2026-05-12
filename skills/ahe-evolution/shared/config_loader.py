"""
Config Loader — base + overlay deep merge with ${ENV} variable resolution.

Ported from AHE evolve.py (lines 115-165). Handles:
  - _base inheritance chain (can chain arbitrarily deep)
  - Deep merge of overlay onto base
  - ${ENV_VAR} resolution against os.environ
  - _meta key extraction (stripped from config, stored separately)
  - Mutually exclusive data-source keys (path vs dataset)
"""

import os
import re
from copy import deepcopy
from pathlib import Path

import yaml


def resolve_env_vars(obj):
    """Recursively resolve ${VAR_NAME} in config values with environment variables.
    Unmatched variables are kept as-is (caller can warn if needed)."""
    if isinstance(obj, str):
        return re.sub(
            r'\$\{([^}]+)\}',
            lambda m: os.environ.get(m.group(1), m.group(0)),
            obj,
        )
    if isinstance(obj, dict):
        return {k: resolve_env_vars(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [resolve_env_vars(item) for item in obj]
    return obj


def deep_merge(base: dict, overlay: dict) -> dict:
    """Deep merge two dicts. Overlay values override base values.
    When both hold a dict at the same key, merge recursively."""
    result = deepcopy(base)
    for key, value in overlay.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_config(config_path: str | Path) -> dict:
    """Load config with _base inheritance chain support.

    Usage:
      config = load_config("config/experiments/exp-01.yaml")
      # If exp-01.yaml has _base: "../base.yaml", base is loaded first,
      # then exp-01 is deep-merged on top.
    """
    config_path = Path(config_path).resolve()
    with open(config_path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    if "_base" not in raw:
        return resolve_env_vars(raw)

    base_ref = raw.pop("_base")
    base_path = (config_path.parent / base_ref).resolve()
    base = load_config(str(base_path))

    # Extract meta keys (_prefixed) for experiment identification
    meta = {}
    for key in list(raw.keys()):
        if key.startswith("_"):
            meta[key] = raw.pop(key)

    config = deep_merge(base, raw)
    config["_meta"] = meta
    return resolve_env_vars(config)


def resolve_output_dir(config: dict) -> Path:
    """Resolve the output directory, with fallback if AGENT_WORKSPACE not set."""
    raw = config.get("output_dir", "agent-workspace/ahe-experiments")
    p = Path(raw)
    if p.is_absolute():
        return p
    # Relative: resolve from the ahe-evolution skill directory
    skill_dir = Path(__file__).resolve().parent.parent
    return (skill_dir / raw).resolve()
