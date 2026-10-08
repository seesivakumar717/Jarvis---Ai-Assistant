"""Loads config.yaml once and exposes it to the rest of the agent."""
import os
import yaml

_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.yaml")

_cache = None


def load_config():
    global _cache
    if _cache is None:
        with open(_CONFIG_PATH, "r") as f:
            _cache = yaml.safe_load(f)
        # expand ~ in filesystem allowlist
        fs = _cache.get("filesystem", {})
        fs["allowed_dirs"] = [os.path.expanduser(p) for p in fs.get("allowed_dirs", [])]
        _cache["filesystem"] = fs
    return _cache
