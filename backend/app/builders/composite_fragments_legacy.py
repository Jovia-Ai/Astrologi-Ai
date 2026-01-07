from __future__ import annotations

from typing import Any, Dict, List


class CompositeFragments:
    def build_fragments(self, composites: List[Dict[str, Any]]) -> Dict[str, Dict[str, Dict[str, Any]]]:
        fragments: Dict[str, Dict[str, Dict[str, Any]]] = {}

        for comp in composites:
            if comp.get("domain") != "identity":
                continue

            fragments["identity"] = self._build_identity_fragments(comp)

        return fragments

    def _build_identity_fragments(self, composite: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """
        GOLDEN PATH v1
        Identity domain icin sabit 3 slot uretir.
        """

        return {
            "cause": {
                "text": "kontrollu bir durus ihtiyaci ile icsel tepkilerin ayni anda calismasi",
                "source": composite["composite_id"],
            },
            "effect": {
                "text": "zamanla icsel gerilim ve iki yonlu hareket hissi olusturmasi",
                "source": composite["composite_id"],
            },
            "shadow": {
                "text": "hangi tarafin yon verdigini kestirememe hissi",
                "source": composite["composite_id"],
            },
        }
