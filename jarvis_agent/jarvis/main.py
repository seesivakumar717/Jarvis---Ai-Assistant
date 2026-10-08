"""Entry point. Text-mode REPL by default; if voice.enabled is set in
config.yaml, swap the input() call for tools.voice.listen_text() once you've
wired that module up.
"""
from jarvis.planner import plan, PlannerError
from jarvis.risk import classify, requires_confirmation
from jarvis.confirm import ask_confirmation, ask_clarifying_question
from jarvis.executor import execute
from jarvis.logger import log_action


def run_step(step: dict):
    action = step["action"]
    args = step.get("args", {})
    reason = step.get("reason", "")
    low_confidence = step.get("confidence", "high") == "low"

    tier = classify(action)
    needs_ok = requires_confirmation(action) or low_confidence

    if needs_ok:
        why = reason or f"this is a {tier}-risk action"
        if low_confidence:
            why += " (and I'm not fully sure this is what you meant)"
        ok = ask_confirmation(action, args, why)
        if not ok:
            log_action(action, args, "cancelled", "user declined")
            print(f"[JARVIS] Skipped: {action}")
            return

    try:
        result = execute(action, args)
        print(f"[JARVIS] Done: {action} -> {result}")
    except Exception as e:
        print(f"[JARVIS] Failed: {action} -> {e}")


def handle_request(user_request: str):
    try:
        parsed = plan(user_request)
    except PlannerError as e:
        print(f"[JARVIS] Couldn't parse a plan from the model: {e}")
        return

    question = parsed.get("clarifying_question")
    if question:
        answer = ask_clarifying_question(question)
        # Re-plan with the clarification folded into the request.
        handle_request(f"{user_request}\n(Clarification: {answer})")
        return

    for step in parsed.get("steps", []):
        run_step(step)


def repl():
    print("JARVIS ready. Type a request, or 'quit' to exit.")
    while True:
        try:
            user_request = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[JARVIS] Shutting down.")
            break
        if user_request.lower() in ("quit", "exit"):
            break
        if not user_request:
            continue
        handle_request(user_request)


if __name__ == "__main__":
    repl()
