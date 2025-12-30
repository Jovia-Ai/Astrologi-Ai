class CompositeFragmentsBuilder:
    """
    GOLDEN PATH v1
    - Identity domain only
    - No scoring
    - No weighting
    - No diversity
    - No potential slot
    """

    def build_fragments(self, composites):
        """
        composites: list of composite dicts from CompositeEngine
        returns: dict { domain: slots }
        """
        fragments = {}

        for comp in composites:
            if comp.get("domain") != "identity":
                continue

            fragments["identity"] = self._build_identity_fragments(comp)

        return fragments

    def _build_identity_fragments(self, composite):
        """
        Produce 3 neutral scene descriptors for NarrativeBuilder.
        NO verbs, NO 'sen', NO astrology terms.
        """

        composite_id = composite.get("composite_id", "unknown")

        return {
            "cause": {
                "text": (
                    "kontrollü ve yapılandırılmış bir duruş ihtiyacı ile "
                    "daha içsel ve tepkisel bir yönün aynı anda aktif olması"
                ),
                "source": composite_id
            },
            "effect": {
                "text": (
                    "iç dünyada iki farklı hareket yönünün birlikte hissedilmesi"
                ),
                "source": composite_id
            },
            "shadow": {
                "text": (
                    "hangi yönün baskın olduğuna dair belirsizlik hissi"
                ),
                "source": composite_id
            }
        }
