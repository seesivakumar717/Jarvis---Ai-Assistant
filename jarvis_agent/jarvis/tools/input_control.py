"""Raw mouse/keyboard control. DISABLED until input_control.enabled: true in config.yaml.

This is intentionally the one tool shipped as a stub. Raw input control is the
capability where a risk-gate bug or a model hallucination does the most
visible damage fastest (typing into the wrong window, clicking something
destructive). Turn it on only after you've run the agent for a while in
text/file/browser-only mode and trust the confirm.py gate.

To enable:
  1. pip install pyautogui pynput
  2. set input_control.enabled: true in config.yaml
  3. uncomment the implementations below
"""
from jarvis.config import load_config


class InputControlDisabled(Exception):
    pass


def _check_enabled():
    cfg = load_config()
    if not cfg.get("input_control", {}).get("enabled", False):
        raise InputControlDisabled(
            "input_control is disabled in config.yaml. Enable it deliberately once you trust the risk gate."
        )


def mouse_click(x: int, y: int) -> str:
    _check_enabled()
    # import pyautogui
    # pyautogui.click(x, y)
    # return f"clicked at ({x}, {y})"
    raise NotImplementedError("Uncomment the pyautogui call above once input_control is enabled.")


def send_keys(text: str) -> str:
    _check_enabled()
    # import pyautogui
    # pyautogui.typewrite(text, interval=0.02)
    # return f"typed {len(text)} chars"
    raise NotImplementedError("Uncomment the pyautogui call above once input_control is enabled.")


def screenshot(save_path: str) -> str:
    _check_enabled()
    # import pyautogui
    # img = pyautogui.screenshot()
    # img.save(save_path)
    # return f"saved screenshot to {save_path}"
    raise NotImplementedError("Uncomment the pyautogui call above once input_control is enabled.")
