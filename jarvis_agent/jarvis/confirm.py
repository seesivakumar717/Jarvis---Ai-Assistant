"""The 'ask you to clear the doubt' gate.

For any medium/high risk action, or any action the planner itself flagged as
low-confidence/ambiguous, this blocks and asks you directly before the
executor is allowed to run it.

Text mode works out of the box. If voice is enabled in config.yaml, this
will also speak the question and listen for your answer — wire that up in
tools/voice.py.
"""
from jarvis.config import load_config


def ask_confirmation(action: str, args: dict, reason: str) -> bool:
    cfg = load_config()
    voice_enabled = cfg.get("voice", {}).get("enabled", False)

    prompt = f"\n[JARVIS] I want to: {action}({args})\nReason this needs your OK: {reason}\nProceed? [y/N] "

    if voice_enabled:
        try:
            from jarvis.tools import voice
            voice.speak(f"I want to {action}. {reason}. Should I proceed?")
            answer = voice.listen_yes_no()
            if answer is not None:
                return answer
        except Exception as e:
            print(f"[JARVIS] Voice confirm failed ({e}), falling back to text.")

    answer = input(prompt).strip().lower()
    return answer in ("y", "yes")


def ask_clarifying_question(question: str) -> str:
    """Used when the planner itself is unsure what you meant, rather than
    unsure about risk. Same escalation path, different trigger."""
    cfg = load_config()
    voice_enabled = cfg.get("voice", {}).get("enabled", False)

    if voice_enabled:
        try:
            from jarvis.tools import voice
            voice.speak(question)
            heard = voice.listen_text()
            if heard:
                return heard
        except Exception as e:
            print(f"[JARVIS] Voice question failed ({e}), falling back to text.")

    return input(f"[JARVIS] {question}\n> ")
