from __future__ import annotations

import re
from typing import List

from .models import LensEnrichment, Rule


def apply_rules_to_event_id(event_id: str, rules: List[Rule]) -> LensEnrichment:
    out = LensEnrichment()
    best_priority = -10**9

    for idx, rule in enumerate(rules):
        pattern = rule.match
        try:
            ok = re.search(pattern, event_id) is not None
        except re.error:
            ok = pattern in event_id

        if not ok:
            continue

        add = rule.add
        out.domains.extend([d for d in add.domains if d not in out.domains])
        out.intents.extend([x for x in add.intents if x not in out.intents])
        out.tags.extend([t for t in add.tags if t not in out.tags])
        out.weight_sum += float(add.weight)

        if add.priority > best_priority:
            best_priority = add.priority
            out.priority = add.priority

        out.evidence.rules.append(f"rule[{idx}]::{pattern}")
        out.evidence.event_ids.append(event_id)

    return out
