from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class MicroExample:
    id: str
    template_tr: str
    valence: str  # "growth" | "repair" | "shadow"
    houses: Set[int]
    modes: Set[str]
    tones: Set[str]


MICRO_EXAMPLES: List[MicroExample] = [
    MicroExample(
        id="m1_growth_1",
        template_tr="Bir ortama girdiginde tonu sessizce toplaman senden.",
        valence="growth",
        houses={1},
        modes={"soft", "neutral", "conj"},
        tones={"Sun", "Saturn", "Uranus", "*"},
    ),
    MicroExample(
        id="m1_repair_1",
        template_tr="Kalabalik arttiginda once kendi eksenini yoklaman cok tipik.",
        valence="repair",
        houses={1},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Neptune", "Uranus", "*"},
    ),
    MicroExample(
        id="m3_growth_1",
        template_tr="Bir cumleyi zihninde tartip sonra daha sade kurman senden.",
        valence="growth",
        houses={3},
        modes={"soft", "neutral", "conj"},
        tones={"Saturn", "Mercury", "Venus", "*"},
    ),
    MicroExample(
        id="m3_growth_2",
        template_tr="Daginik bir fikri icinde toparlayip tek bir cizgiye indirmen senden.",
        valence="growth",
        houses={3},
        modes={"soft", "neutral"},
        tones={"Saturn", "Mercury", "Jupiter", "*"},
    ),
    MicroExample(
        id="m3_repair_1",
        template_tr="Yanlis anlasilma ihtimali hissedince kelimeleri icerde tekrar cevirmen senden.",
        valence="repair",
        houses={3},
        modes={"hard", "conj", "neutral"},
        tones={"Saturn", "Neptune", "Mercury", "*"},
    ),
    MicroExample(
        id="m4_growth_1",
        template_tr="Kendi alanina gecince ritmini hizla toparlaman senden.",
        valence="growth",
        houses={4},
        modes={"soft", "neutral", "conj"},
        tones={"Moon", "Saturn", "Venus", "*"},
    ),
    MicroExample(
        id="m4_repair_1",
        template_tr="Disarisi yorunca once icine cekilip guvenini evde kurman senden.",
        valence="repair",
        houses={4},
        modes={"hard", "neutral", "conj"},
        tones={"Moon", "Saturn", "Mars", "*"},
    ),
    MicroExample(
        id="m5_growth_1",
        template_tr="Bir seyi oyun, keyif ya da yaratim alanina cevirdiginde acilman senden.",
        valence="growth",
        houses={5},
        modes={"soft", "neutral", "conj"},
        tones={"Sun", "Venus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m5_repair_1",
        template_tr="Hevesin dagildiginda once icindeki keyif damarini araman senden.",
        valence="repair",
        houses={5},
        modes={"hard", "neutral"},
        tones={"Sun", "Moon", "Neptune", "*"},
    ),
    MicroExample(
        id="m8_growth_1",
        template_tr="Yakinlik gercek geldigi anda hizla derinlesmen senden.",
        valence="growth",
        houses={7, 8},
        modes={"soft", "conj", "neutral"},
        tones={"Moon", "Venus", "*"},
    ),
    MicroExample(
        id="m8_repair_1",
        template_tr="Yakinlik artinca once icinden yoklayip sonra acilman cok tipik.",
        valence="repair",
        houses={7, 8},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Moon", "Neptune", "*"},
    ),
    MicroExample(
        id="m9_growth_1",
        template_tr="Bir seyi anlamli bir rotaya baglayinca enerjinin buyumesi senden.",
        valence="growth",
        houses={9},
        modes={"soft", "neutral"},
        tones={"Mars", "Uranus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m9_growth_2",
        template_tr="Yonu buldugunda gerisini yolda kurman senden.",
        valence="growth",
        houses={9},
        modes={"soft", "neutral", "conj"},
        tones={"Mercury", "Jupiter", "Mars", "*"},
    ),
    MicroExample(
        id="m9_repair_1",
        template_tr="Cok rota acildiginda once icerde yonunu yeniden toplaman senden.",
        valence="repair",
        houses={9},
        modes={"hard", "neutral"},
        tones={"Saturn", "Uranus", "*"},
    ),
    MicroExample(
        id="m10_growth_1",
        template_tr="Is ciddilestiginde sesi yukseltmek yerine durusunla agirlik koyman senden.",
        valence="growth",
        houses={10},
        modes={"soft", "neutral"},
        tones={"Saturn", "Venus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m10_growth_2",
        template_tr="Dogru anda one cikmadan once icten olcup sonra yerini alman senden.",
        valence="growth",
        houses={10},
        modes={"soft", "neutral", "conj"},
        tones={"Saturn", "Mars", "*"},
    ),
    MicroExample(
        id="m10_repair_1",
        template_tr="Gorunur olma ani yaklasinca once icerden olcup tartman senden.",
        valence="repair",
        houses={10},
        modes={"hard", "neutral"},
        tones={"Saturn", "Neptune", "*"},
    ),
    MicroExample(
        id="m11_growth_1",
        template_tr="Bir grubun icinde kendi yerini sessizce netlestirmen senden.",
        valence="growth",
        houses={11},
        modes={"soft", "neutral"},
        tones={"Saturn", "Venus", "*"},
    ),
    MicroExample(
        id="m11_growth_2",
        template_tr="Insanlari birbirine dogru yerden baglaman senden.",
        valence="growth",
        houses={11},
        modes={"soft", "neutral"},
        tones={"Venus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m11_repair_1",
        template_tr="Kalabalikta once havayi yoklayip sonra rengini koyman senden.",
        valence="repair",
        houses={11},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Neptune", "Mercury", "*"},
    ),
    MicroExample(
        id="m12_growth_1",
        template_tr="Bir seyi once icerde pisirip sonra paylasman senden.",
        valence="growth",
        houses={12},
        modes={"soft", "neutral"},
        tones={"Venus", "Neptune", "Saturn", "*"},
    ),
    MicroExample(
        id="m12_growth_2",
        template_tr="Icinde olgunlasan bir seyi tam zamani gelince disari cikarman senden.",
        valence="growth",
        houses={12},
        modes={"soft", "neutral", "conj"},
        tones={"Neptune", "Saturn", "Moon", "*"},
    ),
    MicroExample(
        id="m12_repair_1",
        template_tr="Hazir hissetmediginde biraz daha icerde tutup olgunlastirman senden.",
        valence="repair",
        houses={12},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Neptune", "*"},
    ),
]


TONE_HINTS_TR: Dict[str, str] = {
    "Saturn": "cerceve ve netlik",
    "Neptune": "sis ve sezgi",
    "Uranus": "elektrik ve yenilik",
    "Mars": "hamle ve cesaret",
    "Venus": "uyum ve zarafet",
    "Jupiter": "genisleme ve firsat",
    "Mercury": "zihin ve ifade",
    "Moon": "duygu ve ihtiyac",
    "Sun": "kimlik ve gorunurluk",
}
