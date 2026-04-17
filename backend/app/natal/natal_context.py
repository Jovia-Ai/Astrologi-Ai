"""NatalContext — natal chart için tek kaynak parsing katmanı.

Faz 1 / Sprint 1.3 çıktısı. Daha önce her engine kendi parsing'ini yapıyordu
(planets/aspects → graph V1, graph V2, primitive engine, dispositor, feature
graph, aspect bundle vb. — her biri ayrı ayrı). Bu sınıf, raw chart dict'inden
**bir kez** türetilen kanonik view'ları sağlar; engine'ler context'i tüketir.

İlk versiyon (Sprint 1.3): Mevcut helper fonksiyonları lazy-wrap eder. Yeni
hesaplama yapmaz — davranış birebir korunur. S1.4'te engine'ler buraya geçer,
S1.6 snapshot test'leri davranış değişimini yakalar.

Sonraki fazlarda (Faz 2): NatalContext genişler — `house_ruler_map`,
`angle_ruler_map`, `dispositor_chain`, `aspect_bundles` gibi türetilmiş
view'lar lazy hesaplanır ve cache'lenir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Mapping, Sequence

from app.helpers.narrative_context import derive_core_aspects, derive_placements
from app.services.chart_service import serialize_aspects, serialize_planets


@dataclass
class NatalContext:
    """Single source of truth for natal chart derived views.

    Engine'ler `chart_data` ham dict'ini değil, bu sınıfın property'lerini
    tüketir. Yeni türetilmiş view eklemek için: yeni bir lazy property ekle,
    `from_chart` içinde init etme — sadece ilk erişimde hesapla.
    """

    chart_data: Mapping[str, Any]
    _planets: List[Dict[str, Any]] | None = field(default=None, init=False, repr=False)
    _aspects: List[Dict[str, Any]] | None = field(default=None, init=False, repr=False)
    _placements: List[str] | None = field(default=None, init=False, repr=False)
    _core_aspects: List[str] | None = field(default=None, init=False, repr=False)
    _angles: Mapping[str, Any] | None = field(default=None, init=False, repr=False)
    _chart_for_selection: Dict[str, Any] | None = field(default=None, init=False, repr=False)

    @classmethod
    def from_chart(cls, chart_data: Mapping[str, Any]) -> "NatalContext":
        return cls(chart_data=chart_data)

    @property
    def angles(self) -> Mapping[str, Any]:
        if self._angles is None:
            raw = self.chart_data.get("angles") if isinstance(self.chart_data, Mapping) else None
            self._angles = raw if isinstance(raw, Mapping) else {}
        return self._angles

    @property
    def planets(self) -> List[Dict[str, Any]]:
        """Canonical planet list. Includes Ascendant as derived point if angles
        provide ascendant_sign and no Ascendant entry exists.
        """
        if self._planets is None:
            planets = serialize_planets(self.chart_data.get("planets", {}))
            angles = self.angles
            if isinstance(angles, Mapping):
                asc_sign = angles.get("ascendant_sign")
                if asc_sign and not any(
                    str(entry.get("planet") or "").strip().lower() == "ascendant"
                    for entry in planets
                    if isinstance(entry, Mapping)
                ):
                    planets.append(
                        {
                            "planet": "Ascendant",
                            "sign": asc_sign,
                            "house": 1,
                            "degree": angles.get("ascendant"),
                            "is_point": True,
                        }
                    )
            self._planets = planets
        return self._planets

    @property
    def aspects(self) -> List[Dict[str, Any]]:
        if self._aspects is None:
            self._aspects = serialize_aspects(self.chart_data.get("aspects", []))
        return self._aspects

    @property
    def placements(self) -> List[str]:
        if self._placements is None:
            self._placements = derive_placements(self.planets)
        return self._placements

    @property
    def core_aspects(self) -> List[str]:
        if self._core_aspects is None:
            self._core_aspects = derive_core_aspects(self.aspects)
        return self._core_aspects

    @property
    def chart_for_selection(self) -> Dict[str, Any]:
        """Selection runtime için normalize edilmiş chart dict.

        `chart_data` ham hali + canonical planets/aspects bağlanmış. Selection
        V3 motorlarının (`build_natal_graph_v2`, `build_natal_feature_graph`,
        `build_primitives_v2`) tek tüketim formatı.
        """
        if self._chart_for_selection is None:
            self._chart_for_selection = {
                **dict(self.chart_data or {}),
                "planets": list(self.planets or []),
                "aspects": list(self.aspects or []),
            }
        return self._chart_for_selection

    def planet_by_name(self, name: str) -> Dict[str, Any] | None:
        """Tek gezegen lookup, case-insensitive."""
        target = name.strip().lower()
        for entry in self.planets:
            if str(entry.get("planet") or "").strip().lower() == target:
                return entry
        return None

    def planets_in_house(self, house: int) -> List[Dict[str, Any]]:
        return [
            entry for entry in self.planets
            if isinstance(entry.get("house"), (int, float)) and int(entry["house"]) == house
        ]

    def planets_in_sign(self, sign: str) -> List[Dict[str, Any]]:
        target = sign.strip().lower()
        return [
            entry for entry in self.planets
            if str(entry.get("sign") or "").strip().lower() == target
        ]

    def aspects_for_planet(self, planet: str) -> List[Dict[str, Any]]:
        target = planet.strip().lower()
        return [
            aspect for aspect in self.aspects
            if (
                str(aspect.get("planet1") or "").strip().lower() == target
                or str(aspect.get("planet2") or "").strip().lower() == target
            )
        ]


__all__ = ["NatalContext"]
