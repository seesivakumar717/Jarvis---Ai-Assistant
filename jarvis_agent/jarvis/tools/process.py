"""Process control, scoped to config.yaml's process.allowed_launch / allowed_kill."""
import subprocess
import psutil
from jarvis.config import load_config


class ProcessNotAllowed(Exception):
    pass


def list_processes() -> list:
    out = []
    for p in psutil.process_iter(["pid", "name"]):
        out.append({"pid": p.info["pid"], "name": p.info["name"]})
    return out


def launch_process(name: str, args: list = None) -> str:
    cfg = load_config()
    allowed = cfg["process"]["allowed_launch"]
    if name not in allowed:
        raise ProcessNotAllowed(f"'{name}' is not in process.allowed_launch: {allowed}")
    cmd = [name] + (args or [])
    subprocess.Popen(cmd)
    return f"launched {cmd}"


def kill_process(name: str) -> str:
    cfg = load_config()
    allowed = cfg["process"]["allowed_kill"]
    never = cfg["process"].get("never_kill", [])
    if name in never:
        raise ProcessNotAllowed(f"'{name}' is in process.never_kill and can never be killed by the agent.")
    if name not in allowed:
        raise ProcessNotAllowed(f"'{name}' is not in process.allowed_kill: {allowed}")
    killed = 0
    for p in psutil.process_iter(["pid", "name"]):
        if p.info["name"] == name:
            p.kill()
            killed += 1
    return f"killed {killed} process(es) named {name}"
