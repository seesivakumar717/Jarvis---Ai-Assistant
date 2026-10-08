"""Classifies a planned action's risk tier using config.yaml's risk_tiers block.

This is the single choke point that decides "just do it" vs "ask the user
first". Keep it dumb and table-driven on purpose — a risk classifier with
clever heuristics is a risk classifier you can't audit at 2am.
"""
from jarvis.config import load_config


def classify(action: str) -> str:
    cfg = load_config()
    tiers = cfg.get("risk_tiers", {})
    for tier_name in ("low", "medium", "high"):
        if action in tiers.get(tier_name, []):
            return tier_name
    # Unknown action = treat as high risk until someone explicitly classifies it.
    return "high"


def requires_confirmation(action: str) -> bool:
    return classify(action) in ("medium", "high")
