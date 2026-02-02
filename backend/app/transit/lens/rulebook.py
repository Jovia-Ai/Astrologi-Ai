from __future__ import annotations

import os
from typing import List

import yaml

from .models import Rule, RuleAdd


def load_domain_rules(path: str) -> List[Rule]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"domain_rules not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    rules_raw = data.get("rules", [])
    rules: List[Rule] = []

    for i, r in enumerate(rules_raw):
        match = str(r.get("match") or "")
        add_raw = r.get("add") or {}
        add = RuleAdd(
            domains=list(add_raw.get("domains") or []),
            intents=list(add_raw.get("intents") or []),
            tags=list(add_raw.get("tags") or []),
            weight=float(add_raw.get("weight") or 0.0),
            priority=int(add_raw.get("priority") or 0),
        )
        rules.append(Rule(match=match, add=add))

    return rules
