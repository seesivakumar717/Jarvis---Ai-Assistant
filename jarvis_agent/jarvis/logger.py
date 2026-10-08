"""Append-only log of every action the agent takes (or refuses to take)."""
import os
import json
import datetime
from jarvis.config import load_config


def _log_path():
    cfg = load_config()
    path = cfg.get("logging", {}).get("path", "logs/actions.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return path


def log_action(action: str, args: dict, status: str, detail: str = ""):
    """status: 'executed' | 'refused' | 'awaiting_confirmation' | 'cancelled' | 'error'"""
    entry = {
        "ts": datetime.datetime.now().isoformat(timespec="seconds"),
        "action": action,
        "args": args,
        "status": status,
        "detail": detail,
    }
    with open(_log_path(), "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry
