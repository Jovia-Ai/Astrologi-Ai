from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set


@dataclass(frozen=True)
class MicroExample:
    id: str
    template_tr: str
    valence: str  # "growth" | "repair" | "shadow"
    houses: Set[int]  # arena houses
    modes: Set[str]  # "soft" | "hard" | "conj" | "neutral"
    tones: Set[str]  # "Saturn" | "Neptune" | ... | "*"


MICRO_EXAMPLES: List[MicroExample] = [
    MicroExample(
        id="m3_growth_1",
        template_tr="Cumleyi kisaltip niyeti netlestirmen; uzatmadan anlasilmayi secmen buradan.",
        valence="growth",
        houses={3},
        modes={"soft", "neutral", "conj"},
        tones={"Saturn", "Mercury", "Venus", "*"},
    ),
    MicroExample(
        id="m3_growth_2",
        template_tr="Konusmayi 2 maddelik yazili ozetle kapatman; 'tamam, burada anlastik' demen buradan.",
        valence="growth",
        houses={3},
        modes={"soft", "neutral"},
        tones={"Saturn", "Mercury", "Jupiter", "*"},
    ),
    MicroExample(
        id="m3_repair_1",
        template_tr="Mesaji yazip silmen; 'yanlis anlasilmayayim' diye tonu tekrar ayarlaman buradan.",
        valence="repair",
        houses={3},
        modes={"hard", "conj", "neutral"},
        tones={"Saturn", "Neptune", "Mercury", "*"},
    ),
    MicroExample(
        id="m3_shadow_1",
        template_tr="Net degilken daha sertlesip cumleyi 'kural' gibi soyleme egilimi buradan.",
        valence="shadow",
        houses={3},
        modes={"hard"},
        tones={"Saturn", "Mars", "*"},
    ),
    MicroExample(
        id="m7_growth_1",
        template_tr="Bir cumleyle sinyal vermen: 'Bunu onemsiyorum' deyip temas kurman buradan.",
        valence="growth",
        houses={7, 8},
        modes={"soft", "neutral"},
        tones={"Venus", "Moon", "*"},
    ),
    MicroExample(
        id="m8_growth_1",
        template_tr="Kirilgan bir seyi kisa ve temiz soylemen; 'su an boyle hissediyorum' demen buradan.",
        valence="growth",
        houses={8},
        modes={"soft", "conj", "neutral"},
        tones={"Moon", "Venus", "*"},
    ),
    MicroExample(
        id="m8_repair_1",
        template_tr="Yakinlik artinca bir anda geri cekilme istegi gelmesi; once guven araman buradan.",
        valence="repair",
        houses={8},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Moon", "Neptune", "*"},
    ),
    MicroExample(
        id="m7_shadow_1",
        template_tr="'Ya hep ya hic' diye icten ice sertlesmen; iliskiyi test etme egilimi buradan.",
        valence="shadow",
        houses={7, 8},
        modes={"hard"},
        tones={"Mars", "Saturn", "*"},
    ),
    MicroExample(
        id="m10_growth_1",
        template_tr="Bir isi 'yayinlanabilir iyi' seviyesinde paylasip akisi baslatman buradan.",
        valence="growth",
        houses={10},
        modes={"soft", "neutral"},
        tones={"Saturn", "Venus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m10_growth_2",
        template_tr="Toplantida tek cumleyle yon vermen; 'bunu soyle yapalim' diye cerceve koyman buradan.",
        valence="growth",
        houses={10},
        modes={"soft", "neutral", "conj"},
        tones={"Saturn", "Mars", "*"},
    ),
    MicroExample(
        id="m10_repair_1",
        template_tr="Gorunur olmaya yaklasinca 'hazir miyim?' diye icten gerilmen buradan.",
        valence="repair",
        houses={10},
        modes={"hard", "neutral"},
        tones={"Saturn", "Neptune", "*"},
    ),
    MicroExample(
        id="m11_growth_1",
        template_tr="Grup planinda rolunu net soylemen; 'ben sunu ustlenirim' deyip duzen kurman buradan.",
        valence="growth",
        houses={11},
        modes={"soft", "neutral"},
        tones={"Saturn", "Venus", "*"},
    ),
    MicroExample(
        id="m11_growth_2",
        template_tr="Bir kisiyi bir kisiyle tanistirman; network'u akillica baglaman buradan.",
        valence="growth",
        houses={11},
        modes={"soft", "neutral"},
        tones={"Venus", "Jupiter", "*"},
    ),
    MicroExample(
        id="m11_repair_1",
        template_tr="Grup icinde yazip sonra sessizlesmen; 'dogru mu soyledim?' diye geri cekilmen buradan.",
        valence="repair",
        houses={11},
        modes={"hard", "neutral", "conj"},
        tones={"Saturn", "Neptune", "Mercury", "*"},
    ),
    MicroExample(
        id="m9_growth_1",
        template_tr="48 saatlik tek sprint secmen; tek ciktiyi tanimlayip yurumeye baslaman buradan.",
        valence="growth",
        houses={9},
        modes={"soft", "neutral"},
        tones={"Mars", "Uranus", "Saturn", "*"},
    ),
    MicroExample(
        id="m9_growth_2",
        template_tr="Bir kaynak listesi degil, tek kaynak secip derinlesmen; rotayi netlestirmen buradan.",
        valence="growth",
        houses={9},
        modes={"soft", "neutral"},
        tones={"Mercury", "Jupiter", "*"},
    ),
    MicroExample(
        id="m9_repair_1",
        template_tr="Ayni anda 3 rota acip yorulman; 'en dogruyu bulmaliyim' diye baslamaman buradan.",
        valence="repair",
        houses={9},
        modes={"hard", "neutral"},
        tones={"Saturn", "Uranus", "*"},
    ),
    MicroExample(
        id="m12_growth_1",
        template_tr="Taslagi once iceride olgunlastirip sonra paylasman; 'pisirip cikman' buradan.",
        valence="growth",
        houses={12},
        modes={"soft", "neutral"},
        tones={"Venus", "Neptune", "Saturn", "*"},
    ),
    MicroExample(
        id="m12_repair_1",
        template_tr="Taslagi kaydedip gondermemen; icerde mukemmellestirmeye takilman buradan.",
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
