"""System-level actions (shutdown, sleep, volume). OS-specific, so these are
thin wrappers you fill in for your platform. All of these are 'high' risk in
config.yaml by default, meaning confirm.py always asks before they run.
"""
import platform
import subprocess


def system_sleep() -> str:
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["pmset", "sleepnow"])
    elif system == "Windows":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif system == "Linux":
        subprocess.run(["systemctl", "suspend"])
    else:
        raise NotImplementedError(f"system_sleep not implemented for {system}")
    return "system going to sleep"


def system_shutdown() -> str:
    system = platform.system()
    if system == "Darwin":
        subprocess.run(["osascript", "-e", 'tell app "System Events" to shut down'])
    elif system == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "0"])
    elif system == "Linux":
        subprocess.run(["systemctl", "poweroff"])
    else:
        raise NotImplementedError(f"system_shutdown not implemented for {system}")
    return "system shutting down"
