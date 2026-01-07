from __future__ import annotations

from typing import Any

from app.builders.phrase_mapper import Claim


def stable_pick(signature: str, variants: list[str]) -> str:
    if not variants:
        return ""
    total = sum(ord(ch) for ch in (signature or "default"))
    return variants[total % len(variants)]


class StylePackV26TR:
    DOMAIN_TITLES = {
        "identity": "Senin Dünyanın İç Çekirdeği",
        "psychology": "Duyguların Nasıl Çalışıyor?",
        "mind": "Zihnin Nasıl Hareket Ediyor?",
        "relationships": "İlişki Tarafında Sen",
        "career": "Dış Dünyada Yolun",
    }

    def title(self, domain: str) -> str:
        return self.DOMAIN_TITLES.get(domain, domain.replace("_", " ").title())

    def recognition(
        self,
        domain: str,
        focus_claims: list[Claim],
        meta_summary: str,
        *,
        signature: str,
    ) -> list[str]:
        if not focus_claims:
            return []
        claim = focus_claims[0]
        payload = claim.payload or {}
        outer = payload.get("outer") or payload.get("outer_mask") or "güçlü"
        inner = payload.get("inner") or payload.get("inner_driver") or "içte daha hassas"
        need = payload.get("need") or "temel ihtiyaç"

        variants = [
            "Sen hayata temkinli başlayan birisin. Dışarıdan güçlü ve kontrollü görünürsün. Ama içeride {inner} daha çok çalışır.",
            "Dışarıdan {outer} gibi durursun. Ama içeride {need} ihtiyacı seni hep bir yere iter.",
        ]
        template = stable_pick(signature, variants)
        return [template.format(outer=outer, inner=inner, need=need)]

    def experienced(self, domain: str, exp_claims: list[Claim], *, signature: str) -> list[str]:
        if not exp_claims:
            return []
        claim = exp_claims[0]
        payload = claim.payload or {}
        strategy = payload.get("strategy") or "temkinli kalma"
        trigger = payload.get("trigger") or payload.get("pattern") or "bir şey tetikleyince"
        inner_question = payload.get("inner_question") or "icimde neyi tutuyorum"

        variants_1 = [
            "Kolay açılmazsın. Önce {strategy} devreye girer; sonra kendini ortaya koyarsın.",
        ]
        variants_2 = [
            "Bazen {trigger} olduğunda, içten içe '{inner_question}' diye yoklarsın.",
        ]
        line_1 = stable_pick(signature + "_exp1", variants_1).format(strategy=strategy)
        line_2 = stable_pick(signature + "_exp2", variants_2).format(
            trigger=trigger, inner_question=inner_question
        )
        return [line_1, line_2]

    def potential(self, domain: str, pot_claims: list[Claim], *, signature: str) -> list[str]:
        payload = pot_claims[0].payload if pot_claims else {}
        growth = payload.get("growth") or "daha dengeli kalmayı"
        mastery = payload.get("mastery") or "gücü daha sakin taşımak"

        variants = [
            "Zamanla şunu öğreniyorsun: {growth}.",
            "Bunu taşımanın olgun formu: {mastery}.",
        ]
        first = stable_pick(signature + "_pot", variants).format(growth=growth, mastery=mastery)
        return [first]

    def shadow(self, domain: str, sh_claims: list[Claim], *, signature: str) -> list[str]:
        if not sh_claims:
            return []
        payload = sh_claims[0].payload or {}
        shadow = payload.get("shadow") or payload.get("shadow_risk") or "yükün ağırlaşması"

        variants = [
            "Zorlandığında, {shadow} daha kolay tetiklenebilir. Bu bir kusur değil; sadece yük binen yerdir.",
        ]
        template = stable_pick(signature + "_sh", variants)
        return [template.format(shadow=shadow)]

    def render_upper(self, ctx: dict[str, Any], upper_content: Any) -> list[str]:
        if not upper_content:
            return []
        if isinstance(upper_content, dict):
            pieces = [upper_content.get("growth_axis"), upper_content.get("mastery_potential")]
            cleaned = [str(piece).strip() for piece in pieces if piece]
            return [" ".join(cleaned)] if cleaned else []
        if isinstance(upper_content, list):
            cleaned = [str(piece).strip() for piece in upper_content if piece]
            return [" ".join(cleaned)] if cleaned else []
        return [str(upper_content)]
