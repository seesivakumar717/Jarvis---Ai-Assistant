"""Turns a natural-language request into a structured action plan by asking
Ollama for JSON only. The model never gets to run anything itself — it just
describes what it wants done, and risk.py/confirm.py/executor.py decide
whether and how that actually happens.
"""
import json
import re
import requests
from jarvis.config import load_config
from jarvis.executor import ACTIONS

SYSTEM_PROMPT = f"""You are the planning module of a local automation agent called JARVIS.

You do not execute anything yourself. You only decide what should happen next
and describe it as JSON. A separate system will check permissions, ask the
user for confirmation on risky actions, and only then execute.

Available actions: {", ".join(sorted(ACTIONS.keys()))}

Respond with ONLY a JSON object, no prose, no markdown fences, in this exact shape:

{{
  "steps": [
    {{"action": "<one of the available actions>", "args": {{...}}, "confidence": "high|low", "reason": "<short reason>"}}
  ],
  "clarifying_question": "<ask this instead, if the request is too ambiguous to plan at all>"
}}

Rules:
- If the request is clear, fill "steps" and leave "clarifying_question" empty.
- If you genuinely can't tell what the user wants (e.g. which file, which app,
  which site), leave "steps" empty and put a specific question in
  "clarifying_question". Don't guess at destructive or irreversible actions.
- Mark "confidence": "low" on any step you're not sure about, even if you're
  including it — the agent will pause and ask the user about it specifically.
- Only use actions from the available list above. Never invent new ones.
"""


class PlannerError(Exception):
    pass


def _extract_json(text: str) -> dict:
    # Strip accidental code fences if the model adds them anyway.
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise PlannerError(f"Model did not return valid JSON: {e}\nRaw output: {text[:500]}")


def plan(user_request: str) -> dict:
    cfg = load_config()["ollama"]
    resp = requests.post(
        f"{cfg['host']}/api/chat",
        json={
            "model": cfg["model"],
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_request},
            ],
            "stream": False,
            "options": {"temperature": cfg.get("temperature", 0.2)},
        },
        timeout=120,
    )
    resp.raise_for_status()
    content = resp.json()["message"]["content"]
    return _extract_json(content)
