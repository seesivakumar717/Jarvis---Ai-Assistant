"""File system tool, hard-scoped to config.yaml's filesystem.allowed_dirs.

Every function re-validates the path itself — never trust that a caller
upstream already checked, since that's exactly the kind of assumption that
turns into "oops, deleted something outside the sandbox".
"""
import os
from jarvis.config import load_config


class PathNotAllowed(Exception):
    pass


def _resolve_and_check(path: str) -> str:
    cfg = load_config()
    allowed = cfg["filesystem"]["allowed_dirs"]
    full = os.path.realpath(os.path.expanduser(path))
    for d in allowed:
        d_real = os.path.realpath(d)
        if full == d_real or full.startswith(d_real + os.sep):
            return full
    raise PathNotAllowed(
        f"'{path}' resolves outside allowed_dirs {allowed}. "
        f"Add it to config.yaml if this should be permitted."
    )


def list_files(directory: str) -> list:
    full = _resolve_and_check(directory)
    if not os.path.isdir(full):
        raise NotADirectoryError(full)
    return sorted(os.listdir(full))


def read_file(path: str) -> str:
    full = _resolve_and_check(path)
    with open(full, "r", errors="replace") as f:
        return f.read()


def write_file(path: str, content: str, append: bool = False) -> str:
    full = _resolve_and_check(path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    mode = "a" if append else "w"
    with open(full, mode) as f:
        f.write(content)
    return f"wrote {len(content)} chars to {full}"


def delete_file(path: str) -> str:
    cfg = load_config()
    full = _resolve_and_check(path)
    protected = cfg["filesystem"].get("protected_extensions", [])
    if any(full.endswith(ext) for ext in protected):
        raise PermissionError(f"{full} has a protected extension and cannot be deleted by the agent.")
    if not os.path.isfile(full):
        raise FileNotFoundError(full)
    os.remove(full)
    return f"deleted {full}"
