from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple
import hashlib
import re

from app.narrative.voice_guardrails_tr import (
    find_forbidden_public_copy_issues,
    find_organic_period_copy_issues,
    find_technical_leakage,
)
from app.transit.narrative import phrase_lib_tr
from app.transit.narrative.canonical_natal_activation import (
    build_period_prefix_from_period_spine,
    select_period_theme_from_spine,
)
from app.transit.narrative.period_semantic_focus import (
    PeriodSemanticFocusResult,
    resolve_period_semantic_focus,
)
from app.transit.narrative.period_voice_policy import build_period_voice_policy
from app.transit.narrative import text_quality_tr
from app.transit.narrative.natal_promise import HOUSE_DOMAIN_HINTS

TRACK_IDS = {
    "identity_spine",
    "method_shift_9_virgo",
    "network_transform_11",
    "mirror_axis_1_7",
    "resource_axis_2_8",
    "healing_axis_6_12",
    "creativity_5",
    "root_4",
    "dissolution_12",
    "default",
}
ANGLE_POINTS = {"ASC", "DSC", "MC", "IC"}

RULERS = {
    "Aries": "Mars",
    "Taurus": "Venus",
    "Gemini": "Mercury",
    "Cancer": "Moon",
    "Leo": "Sun",
    "Virgo": "Mercury",
    "Libra": "Venus",
    "Scorpio": "Mars",
    "Sagittarius": "Jupiter",
    "Capricorn": "Saturn",
    "Aquarius": "Saturn",
    "Pisces": "Jupiter",
}

HOUSE_THEME_TR: Dict[int, str] = {
    1: "kimlik ve duruş",
    2: "değer ve kaynaklar",
    3: "zihin ve iletişim",
    4: "temel düzen ve güven",
    5: "yaratıcılık ve ifade",
    6: "günlük ritim ve emek",
    7: "ilişkiler ve sözleşme",
    8: "derin bağlar ve güven",
    9: "ufuk, öğrenme ve yön",
    10: "kariyer yönü ve görünürlük",
    11: "topluluk, network ve hedefler",
    12: "iç dünya ve bırakış",
}

ANGLE_TO_CUSP_HOUSE = {"ASC": 1, "DSC": 7, "MC": 10, "IC": 4}

CHAPTER_ROLE_OPENING_TR = {
    "opener": "Kapıyı ilk aralayan hareket burada başlıyor.",
    "builder": "Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor.",
    "peak": "Görünür olan eşik tam bu hatta toplanıyor.",
    "release": "Aynı sıkılıkta taşınmayan şey önce burada belli oluyor.",
    "integrator": "Dağınık duran parçalar burada tek çizgide toplanmak istiyor.",
}

CHAPTER_ROLE_BUILD_TR = {
    "opener": "Süreç, ilk hamleyi bilinçli atmayı öğretiyor.",
    "builder": "Süreç, kalıcı bir iskelet kurmayı öğretiyor.",
    "peak": "Süreç, görünür olan şeyi yönetmeyi öğretiyor.",
    "release": "Süreç, artık taşınmayan yükü bırakmayı öğretiyor.",
    "integrator": "Süreç, dağılmış parçaları tek bir ritimde birleştirmeyi öğretiyor.",
}

_PERIOD_POLICY_ROLE_COPY = {
    "opener": "Bu daha çok kapıyı aralayan ilk hareket gibi çalışıyor.",
    "builder": "Bu yüzden hikaye hızlı bir sonuçtan çok, yavaş kurulan bir omurga gibi ilerliyor.",
    "peak": "Bu kez konu daha görünür; ertelediğin ayrım kendini daha açık gösteriyor.",
    "release": "Burada asıl hareket, artık aynı biçimde taşımadığın şeyi fark etmek.",
    "integrator": "Bu etki ayrı duran parçaları aynı ritme topluyor.",
}

_PERIOD_POLICY_SLOT_COPY = {
    "work_visibility_courage_process": (
        "Bu dönem dışarıda daha çok yer kaplaman gerekiyor. Bu sadece görünür olmak değil; "
        "yaptığın şeyin arkasında durma biçimin değişiyor."
    ),
    "work_visibility_courage_meaning": (
        "İçeride bir tarafın hâlâ hazır olup olmadığına bakabilir, ama tema artık beklemekten çok "
        "kendini göstermeye dönüyor."
    ),
    "work_visibility_courage_edge": "Buradaki eşik, görünürlüğü kusursuzluk şartına bağlamamak.",
    "work_visibility_courage_build": "Sende daha cesur ve daha temiz bir görünürlük kuruyor.",
    "work_visibility_courage_reason": (
        "Bu konu boşuna buradan açılmıyor; sende görünürlük zaten cesaretle iç ölçünün birlikte çalıştığı bir alan."
    ),
    "work_visibility_responsibility_process": (
        "Bu dönem senden daha fazla netlik bekleniyor. İş, rol ya da sorumluluk tarafında "
        "taşıdığın şeyler daha görünür hale geliyor."
    ),
    "work_visibility_responsibility_meaning": (
        "Bu baskı sadece yükün artması değil; hangi yükün gerçekten sana ait olduğunu ayırman."
    ),
    "work_visibility_responsibility_edge": "Buradaki eşik, alışkanlıktan taşıdığın şeyi görev sanmamak.",
    "work_visibility_responsibility_build": (
        "Sende daha olgun bir sorumluluk duygusu kuruyor; taşıdığın şeyin adını daha net koyuyorsun."
    ),
    "work_visibility_responsibility_reason": (
        "Bu konu boşuna buradan açılmıyor; sende görünürlük zaten sorumlulukla birlikte çalışıyor."
    ),
    "work_visibility_control_process": (
        "Bu dönem iş, yön ya da görünürlük tarafında kontrol etmek istediğin yerler belirginleşiyor. "
        "Bir şeyi sıkı tutman sadece hırs değil; orada kaybetmek istemediğin bir güç alanı var."
    ),
    "work_visibility_control_meaning": (
        "Asıl mesele daha fazla kontrol kurmak değil; hangi alanı gerçekten yönetmen, hangisini akışa bırakman gerektiğini ayırmak."
    ),
    "work_visibility_control_edge": "Buradaki eşik, gücü sadece sıkı tutmakla karıştırmamak.",
    "work_visibility_control_build": "Sende daha sakin ama daha etkili bir otorite kuruyor.",
    "work_visibility_control_reason": (
        "Bu konu boşuna buradan açılmıyor; sende görünürlük zaten güç, kontrol ve güven temasıyla birlikte çalışıyor."
    ),
    "work_visibility_default_process": (
        "Bu dönem dışarıda nasıl durduğun daha çok dikkat çekiyor. Asıl değişen, neyi gerçekten sahiplendiğin."
    ),
    "work_visibility_default_meaning": (
        "Sırf alıştığın için taşıdığın şeylerle, artık içinden gelerek yaptığın şeyler birbirinden ayrılmaya başlıyor."
    ),
    "work_visibility_default_edge": "Buradaki eşik, dışarıdaki rolü içerideki niyetin yerine koymamak.",
    "work_visibility_default_build": "Sende daha net bir duruş kuruyor; görünürlük biraz daha seçilmiş hale geliyor.",
    "work_visibility_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende dışarıdaki rol ile iç niyet aynı anda çalışıyor."
    ),
    "relational_intimacy_process": (
        "Bu dönem yakınlık kurduğun yerlerde daha gerçek davranıyorsun. Birine yaklaşırken sadece "
        "ne hissettiğin değil, ne kadar açık kalabildiğin de görünür oluyor."
    ),
    "relational_intimacy_meaning": (
        "Bu tema ilişki yaşamakla sınırlı değil; ilişkide kendini kaybetmeden kalmayı öğreniyorsun."
    ),
    "relational_intimacy_edge": "Buradaki eşik, korunmayı tamamen kapanmaya çevirmemek.",
    "relational_intimacy_build": "Sende daha temiz bir yakınlık dili kuruyor; kapanmadan seçici kalabiliyorsun.",
    "relational_intimacy_reason": (
        "Bu konu boşuna buradan açılmıyor; sende yakınlık zaten güven ve seçimle birlikte çalışıyor."
    ),
    "relational_closeness_process": (
        "Bu dönem yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında kalmak, konuşmak ya da açılmak "
        "daha küçük ama daha gerçek temaslar üzerinden çalışıyor."
    ),
    "relational_closeness_meaning": (
        "Buradaki tema romantik ya da sosyal bir yakınlıkla sınırlı değil; bir bağın içinde kendini yumuşatırken kaybolmamayı öğreniyorsun."
    ),
    "relational_closeness_edge": "Buradaki eşik, yakınlığı hemen tam açıklık sanmamak.",
    "relational_closeness_build": "Sende daha sıcak ama daha seçimli bir yakınlık dili kuruyor.",
    "relational_closeness_reason": (
        "Bu konu boşuna buradan açılmıyor; sende yakınlık zaten güven, açıklık ve kendini koruma biçiminle birlikte çalışıyor."
    ),
    "relational_responsibility_process": (
        "Bu dönem ilişkilerde sınır daha belirgin hale geliyor. Eskiden görmezden geldiğin küçük "
        "rahatsızlıklar şimdi daha net konuşuyor olabilir."
    ),
    "relational_responsibility_meaning": (
        "Bu bağdan uzaklaştığın anlamına gelmiyor; yakınlığın içinde kendine ait bir alan istiyorsun."
    ),
    "relational_responsibility_edge": "Buradaki eşik, mesafeyi ceza gibi değil, düzen gibi kurmak.",
    "relational_responsibility_build": "Sende güveni daha yavaş ama daha sağlam kuran bir ilişki ritmi oluşturuyor.",
    "relational_responsibility_reason": (
        "Bu konu boşuna buradan açılmıyor; sende yakınlık zaten sınır ve güvenle birlikte çalışıyor."
    ),
    "relational_boundary_process": (
        "Bu dönem ilişkilerde sınır daha belirgin hale geliyor. Açılmak istediğin yerle kendini "
        "koruduğun yer aynı anda görünür oluyor."
    ),
    "relational_boundary_meaning": (
        "Yakınlıkla mesafe birbirinin zıttı gibi durabilir, ama bu dönem ikisini aynı cümlede tutmayı öğreniyorsun."
    ),
    "relational_boundary_edge": "Buradaki eşik, beklemeyi netlik sanmak.",
    "relational_boundary_build": "Sende daha seçici ama daha gerçek bir temas biçimi kuruyor.",
    "relational_boundary_reason": (
        "Bu konu boşuna buradan açılmıyor; sende yakınlık zaten eşik ve açıklık arasında çalışıyor."
    ),
    "relational_default_process": (
        "Bu dönem yakın olduğun yerlerde daha çok kendin oluyorsun. Birinin yanında durmak ya da "
        "durmamak eskisi kadar yarım his bırakmıyor."
    ),
    "relational_default_meaning": (
        "Açılırken de korunurken de daha bilinçlisin; ikisinin birbirinin zıttı olmadığını fark ediyorsun."
    ),
    "relational_default_edge": "Buradaki eşik, yakınlığı kendinden uzaklaşmak sanmamak.",
    "relational_default_build": "Sende daha sakin ve daha gerçek bir yakınlık alanı kuruyor.",
    "relational_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende bağ kurmak zaten kendini koruma biçiminle birlikte çalışıyor."
    ),
    "shadow_protection_control_process": (
        "Bu dönem kontrol etmek istediğin yerler daha belirginleşiyor. Bir şeyi sıkı tutman boşuna değil; "
        "orada güven, kayıp ya da hazırlıksız yakalanma teması olabilir."
    ),
    "shadow_protection_control_meaning": "Aynı mekanizma seni korurken hareketini de yavaşlatabilir.",
    "shadow_protection_control_edge": (
        "Buradaki eşik, kontrolü tamamen bırakmak değil; nerede işe yaradığını, nerede seni geciktirdiğini ayırmak."
    ),
    "shadow_protection_control_build": (
        "Sende daha bilinçli bir iç düzen kuruyor; kendini kapatmadan da koruyabildiğin bir çizgi oluşuyor."
    ),
    "shadow_protection_control_reason": (
        "Bu konu boşuna buradan açılmıyor; sende koruma refleksi zaten güç ve güven temasıyla birlikte çalışıyor."
    ),
    "shadow_protection_dissolution_process": (
        "Bu dönem dışarıda büyük bir şey olmuyor gibi durabilir. İçeride ise bir sınırın nerede başlayıp "
        "nerede bittiğini daha dikkatle izliyorsun."
    ),
    "shadow_protection_dissolution_meaning": (
        "Belirsizlik burada boşluk değil; neyi artık hisle, neyi netlikle taşıyacağını ayıran bir alan."
    ),
    "shadow_protection_dissolution_edge": "Buradaki eşik, muğlaklığı tek başına sezgiyle yönetmeye çalışmak.",
    "shadow_protection_dissolution_build": "Sende daha yumuşak ama daha seçici bir koruma biçimi kuruyor.",
    "shadow_protection_dissolution_reason": (
        "Bu konu boşuna buradan açılmıyor; sende iç sınır zaten hassasiyet ve korunma ihtiyacıyla birlikte çalışıyor."
    ),
    "shadow_protection_default_process": (
        "Bu dönem kendini koruma biçimin daha görünür oluyor. Dışarıda büyük bir şey olmuyor gibi dursa da, "
        "içeride daha dikkatli duran bir tarafın var."
    ),
    "shadow_protection_default_meaning": (
        "Bunun hep çözülmesi gereken bir şey olması gerekmiyor; bazen seni uzun zamandır taşıyan bir tarafına ilk kez net bakıyorsun."
    ),
    "shadow_protection_default_edge": "Buradaki eşik, korunmayı ilerlemenin yerine koymak.",
    "shadow_protection_default_build": "Sende daha seçimli bir iç düzen kuruyor; artık sadece otomatik değil, daha bilinçli.",
    "shadow_protection_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende korunma refleksi zaten karakter mimarisinin önemli bir parçası."
    ),
    "growth_integration_change_process": "Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirini daha çok duyuyor.",
    "growth_integration_change_meaning": (
        "Yeni bir taraf edinmekten çok, sende olan parçaları aynı hayatın içine yerleştiriyorsun."
    ),
    "growth_integration_change_edge": "Buradaki eşik, değişimi her şeyi bozmak sanmak.",
    "growth_integration_change_build": "Sende daha esnek ama dağılmayan bir yön duygusu kuruyor.",
    "growth_integration_change_reason": (
        "Bu konu boşuna buradan açılmıyor; sende büyüme zaten farklı parçaları aynı ritme alma ihtiyacıyla çalışıyor."
    ),
    "growth_integration_responsibility_process": (
        "Bu dönem sende ayrı duran parçalar daha düzenli bir omurga arıyor. Disiplinle esneklik aynı hayatın içinde yer bulmaya çalışıyor."
    ),
    "growth_integration_responsibility_meaning": (
        "Buradaki mesele daha çok yük almak değil; zaten bildiklerini birlikte yaşayabilecek bir düzen kurmak."
    ),
    "growth_integration_responsibility_edge": "Buradaki eşik, her parçayı tek başına kusursuzlaştırmaya çalışmak.",
    "growth_integration_responsibility_build": "Sende daha bütünlüklü ve daha taşınabilir bir yapı kuruyor.",
    "growth_integration_responsibility_reason": (
        "Bu konu boşuna buradan açılmıyor; sende olgunlaşma zaten parça parça değil, bütün bir düzen olarak çalışıyor."
    ),
    "growth_integration_default_process": "Sende zaten çalışan birkaç ayrı taraf var. Bu dönem onlar birbirine daha yakın duruyor.",
    "growth_integration_default_meaning": (
        "Yeni bir şey öğrenmek değil bu; zaten sende olan şeyleri birlikte taşımayı öğreniyorsun."
    ),
    "growth_integration_default_edge": "Buradaki eşik, aynı anda çalışan taraflarını çelişki sanmak.",
    "growth_integration_default_build": (
        "Sende daha bütünlüklü bir yön kuruyor; içeride ayrı konuşan parçalar aynı cümlede toplanıyor."
    ),
    "growth_integration_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende büyüme zaten farklı taraflarını aynı hayata yerleştirme ihtiyacıyla çalışıyor."
    ),
    "emotional_regulation_regulation_process": (
        "Bu dönem duygusal ritmin daha görünür hale geliyor. Ne zaman açıldığın, ne zaman geri çekildiğin ve neyle sakinleştiğin "
        "daha net seçiliyor."
    ),
    "emotional_regulation_regulation_meaning": (
        "Bu sadece hassasiyetin artması değil; içerideki dalgayı daha iyi okuyup ona uygun bir düzen kurma ihtiyacı."
    ),
    "emotional_regulation_regulation_edge": "Buradaki eşik, her duyguyu hemen karar gibi almak.",
    "emotional_regulation_regulation_build": "Sende daha duyarlı ama daha taşınabilir bir iç ritim kuruyor.",
    "emotional_regulation_regulation_reason": (
        "Bu konu boşuna buradan açılmıyor; sende duygusal güven zaten ritim, ihtiyaç ve iç düzenle birlikte çalışıyor."
    ),
    "emotional_regulation_default_process": (
        "Bu dönem içerideki düzen daha çok dikkat istiyor. Bedenin, duyguların ve günlük ritmin aynı anda konuşuyor olabilir."
    ),
    "emotional_regulation_default_meaning": (
        "Asıl mesele kendini zorlamak değil; seni gerçekten sakinleştiren ritmi yeniden tanımak."
    ),
    "emotional_regulation_default_edge": "Buradaki eşik, düzeni sadece kontrol etmek sanmak.",
    "emotional_regulation_default_build": "Sende daha gerçekçi ve daha yumuşak bir iç denge kuruyor.",
    "emotional_regulation_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende iç güven zaten günlük ritim ve duygu düzeninle birlikte çalışıyor."
    ),
    "primary_identity_courage_process": (
        "Bu dönem kendini daha net ortaya koyman gerekiyor. Bu büyük bir çıkış yapmak değil; nerede durduğunu daha açık göstermek."
    ),
    "primary_identity_courage_meaning": (
        "İçeride bir tarafın hâlâ ölçüp biçebilir, ama tema artık kendi enerjini saklamadan yön vermeye dönüyor."
    ),
    "primary_identity_courage_edge": "Buradaki eşik, cesareti sadece yüksek sesle görünmek sanmamak.",
    "primary_identity_courage_build": "Sende daha canlı ve daha sahiplenilmiş bir duruş kuruyor.",
    "primary_identity_courage_reason": (
        "Bu konu boşuna buradan açılmıyor; sende kimlik zaten cesaret, yön ve kendini ortaya koyma ihtiyacıyla birlikte çalışıyor."
    ),
    "primary_identity_default_process": (
        "Bu dönem kimlik ve duruş hattında daha net bir ayrım var. Neyi gerçekten sen taşıyorsun, neyi alışkanlıktan sürdürüyorsun?"
    ),
    "primary_identity_default_meaning": "Buradaki mesele kendini yeniden icat etmek değil; zaten olan tarafını daha bilinçli kullanmak.",
    "primary_identity_default_edge": "Buradaki eşik, duruşu savunmaya çevirmemek.",
    "primary_identity_default_build": "Sende daha sade ve daha seçilmiş bir benlik hissi kuruyor.",
    "primary_identity_default_reason": (
        "Bu konu boşuna buradan açılmıyor; sende kimlik zaten yön, irade ve kendini taşıma biçiminle birlikte çalışıyor."
    ),
    "generic_control_process": (
        "Bu dönem kontrol etmek istediğin yer daha çok görünür oluyor. Orada güç kadar güven ihtiyacı da var."
    ),
    "generic_control_meaning": "Asıl mesele kontrolü bırakmak değil; nerede koruduğunu, nerede seni daralttığını ayırmak.",
    "generic_control_edge": "Buradaki eşik, sıkı tutmayı tek güvenlik yolu sanmamak.",
    "generic_control_build": "Sende daha bilinçli bir güç kullanımı kuruyor.",
    "generic_control_reason": "Bu konu boşuna buradan açılmıyor; sende bu tema güç ve güven ihtiyacına bağlanıyor.",
    "generic_dissolution_process": "Bu dönem bazı sınırlar daha yumuşak ya da belirsiz hissedilebilir.",
    "generic_dissolution_meaning": "Belirsizlik burada boşluk değil; neyin çözülüp neyin kalacağını ayıran bir alan.",
    "generic_dissolution_edge": "Buradaki eşik, muğlaklığı tek başına sezgiyle yönetmeye çalışmak.",
    "generic_dissolution_build": "Sende daha yumuşak ama daha seçici bir farkındalık kuruyor.",
    "generic_dissolution_reason": "Bu konu boşuna buradan açılmıyor; sende hassasiyet ve sınır teması birlikte çalışıyor.",
    "generic_change_process": "Bu dönem alıştığın ritim değişmek istiyor. Eski düzenin bazı yerleri artık aynı hızda taşınmıyor.",
    "generic_change_meaning": "Bu kırılma sadece değişiklik değil; daha canlı bir düzen kurma ihtiyacı.",
    "generic_change_edge": "Buradaki eşik, değişimi her şeyi bozmak sanmak.",
    "generic_change_build": "Sende daha esnek ve daha uyanık bir yön duygusu kuruyor.",
    "generic_change_reason": "Bu konu boşuna buradan açılmıyor; sende büyüme zaten ritim değiştirme cesaretiyle çalışıyor.",
    "generic_courage_process": "Bu dönem daha açık bir hamle istiyor. Kendini geri tutan yerle hareket etmek isteyen yer aynı anda görünür.",
    "generic_courage_meaning": "Cesaret burada kendini zorlamak değil; enerjini daha dürüst bir yöne koymak.",
    "generic_courage_edge": "Buradaki eşik, hazır hissetmeyi başlama şartı yapmak.",
    "generic_courage_build": "Sende daha canlı ve daha doğrudan bir hareket alanı kuruyor.",
    "generic_courage_reason": "Bu konu boşuna buradan açılmıyor; sende bu tema irade ve yön duygusuna bağlanıyor.",
    "generic_closeness_process": "Bu dönem yakınlık daha küçük ama daha gerçek temaslar üzerinden çalışıyor.",
    "generic_closeness_meaning": "Buradaki mesele sadece birine yaklaşmak değil; yaklaşırken kendini kaybetmemek.",
    "generic_closeness_edge": "Buradaki eşik, yakınlığı tamamen açıklık ya da tamamen kapanma gibi yaşamak.",
    "generic_closeness_build": "Sende daha seçici ve daha sıcak bir temas biçimi kuruyor.",
    "generic_closeness_reason": "Bu konu boşuna buradan açılmıyor; sende bağ kurmak güven ve açıklıkla birlikte çalışıyor.",
    "generic_regulation_process": "Bu dönem iç ritmin daha fazla dikkat istiyor. Ne seni yükseltiyor, ne seni sakinleştiriyor daha netleşiyor.",
    "generic_regulation_meaning": "Bu sadece duygusal dalgalanma değil; kendini taşıma biçimini yeniden ayarlama ihtiyacı.",
    "generic_regulation_edge": "Buradaki eşik, her duygusal dalgayı hemen karar gibi almak.",
    "generic_regulation_build": "Sende daha taşınabilir bir iç denge kuruyor.",
    "generic_regulation_reason": "Bu konu boşuna buradan açılmıyor; sende duygu ve güven teması birlikte çalışıyor.",
}


@dataclass(frozen=True)
class PeriodStoryContext:
    period_core: Dict[str, Any]
    chart_snapshot: Dict[str, Any]
    natal_promise: Dict[str, Any]
    canonical_period_spine: Dict[str, Any] | None = None
    active_life_chapter: Mapping[str, Any] | None = None
    semantic_focus_result: PeriodSemanticFocusResult | None = None
    locale: str = "tr"
    enable_fun: bool = True
    recent_rhetorical_frames: Sequence[str] = ()
    recent_valence_modes: Sequence[str] = ()


@dataclass(frozen=True)
class PeriodNarrative:
    period_reading_v1: Dict[str, Any]
    period_opening: str
    big_picture: str
    mechanism: str
    growth_edge: str
    relational_or_life_expression: str
    what_it_builds: str
    upper_meaning: str
    debug: Dict[str, Any]


def infer_story_track_id(
    card: Mapping[str, Any],
    period_root_causes: Optional[Sequence[Mapping[str, Any]]] = None,
) -> str:
    event_id = str(card.get("event_id") or "").strip()
    if period_root_causes and event_id:
        best_key = ""
        best_score = -1.0
        for rc in period_root_causes:
            key = str(rc.get("key") or "").strip()
            if key not in TRACK_IDS:
                continue
            score = _safe_float(rc.get("score"), 0.0)
            evidence = rc.get("evidence") if isinstance(rc.get("evidence"), Sequence) else []
            evidence_tokens = {str(x).strip() for x in evidence}
            if event_id in evidence_tokens and score > best_score:
                best_key = key
                best_score = score
        if best_key:
            return best_key

    transit_body = str(card.get("transit_body") or "").strip().lower()
    aspect = str(card.get("aspect") or "").strip().lower()
    target = str(card.get("natal_point") or "").strip().upper()

    if target == "DSC":
        return "mirror_axis_1_7"
    if transit_body == "neptune" and target in ANGLE_POINTS and aspect in {"square", "opposition"}:
        return "identity_spine" if target == "ASC" else "mirror_axis_1_7"
    if transit_body == "uranus":
        return "method_shift_9_virgo"
    if transit_body == "pluto" or target == "PLUTO":
        return "network_transform_11"

    # S0-3b: natal-house fallback rules. Sırasıyla: dissolution (Neptune × 12 keskin
    # imza), healing (6/12 catch-all), resource (2/8), creativity (5), root (4).
    # Deterministic; ilk match kazanır. House okuması yoksa default'a düşer.
    houses = card.get("houses")
    transit_in_natal_house = None
    if isinstance(houses, Mapping):
        transit_in_natal_house = _safe_int(houses.get("transit_in_natal_house"))

    if transit_body == "neptune" and transit_in_natal_house == 12:
        return "dissolution_12"
    if transit_in_natal_house in {6, 12}:
        return "healing_axis_6_12"
    if transit_in_natal_house in {2, 8}:
        return "resource_axis_2_8"
    if transit_in_natal_house == 5:
        return "creativity_5"
    if transit_in_natal_house == 4:
        return "root_4"

    return "default"


def build_story_track_copy(track_id: str, card: Mapping[str, Any]) -> Dict[str, Any]:
    packs = getattr(phrase_lib_tr, "PERIOD_TRACK_COPY_TR", {})
    pack = packs.get(track_id) or packs.get("default") or {}
    seed = str(card.get("event_id") or track_id)

    vars_map = {
        "planet_hook": _build_planet_hook_tr(
            transit_body=str(card.get("transit_body") or ""),
            aspect=str(card.get("aspect") or ""),
            target=str(card.get("natal_point") or ""),
        ),
        "spine_label": str(card.get("signature_tr") or card.get("signature") or "").strip(),
        "start_house_tr": HOUSE_THEME_TR.get(_safe_int((card.get("scene") or {}).get("start_house")) or 3, ""),
        "outcome_house_tr": HOUSE_THEME_TR.get(_safe_int((card.get("scene") or {}).get("outcome_house")) or 1, ""),
    }

    opening = _render_track_variant(pack.get("period_opening") or pack.get("lead"), seed, "opening", vars_map)
    big = _render_track_variant(pack.get("big_picture"), seed, "big", vars_map)
    mech = _render_track_variant(pack.get("mechanism"), seed, "mech", vars_map)
    growth = _render_track_variant(pack.get("growth_edge") or pack.get("contribution"), seed, "growth", vars_map)
    life = _render_track_variant(pack.get("relational_or_life_expression") or pack.get("mechanism"), seed, "life", vars_map)
    builds = _render_track_variant(pack.get("what_it_builds") or pack.get("contribution"), seed, "builds", vars_map)

    return {
        "track_id": track_id,
        "version": str(pack.get("version") or "period_story_v2"),
        "lead": _final_polish_tr(opening),
        "period_opening": _final_polish_tr(opening),
        "big_picture": _final_polish_tr(big),
        "mechanism": _final_polish_tr(mech),
        "growth_edge": _final_polish_tr(growth),
        "relational_or_life_expression": _final_polish_tr(life),
        "what_it_builds": _final_polish_tr(builds),
        "contribution": _final_polish_tr(builds),
        "upper_meaning": _final_polish_tr(builds),
    }


def build_period_story(ctx: PeriodStoryContext) -> PeriodNarrative:
    spine, supports = _select_spine_and_supports(ctx.period_core)
    root_causes = ctx.period_core.get("_debug_root_causes") if isinstance(ctx.period_core.get("_debug_root_causes"), list) else []
    track_id = infer_story_track_id(spine, root_causes)
    track_story = build_story_track_copy(track_id, spine)
    policy_events = _period_voice_policy_events(ctx.canonical_period_spine, spine, supports)
    semantic_focus_result = _ensure_semantic_focus_result(
        ctx,
        matched_events=policy_events,
        chapter_role=_chapter_role_name(spine),
    )
    semantic_focus_debug = (
        semantic_focus_result.to_debug_dict(include_evidence=False)
        if isinstance(semantic_focus_result, PeriodSemanticFocusResult)
        else {}
    )
    period_voice_policy = build_period_voice_policy(
        canonical_period_spine=ctx.canonical_period_spine,
        matched_events=policy_events,
        chapter_role=_chapter_role_name(spine),
        canonical_backing_node_ids=_canonical_backing_node_ids(ctx.canonical_period_spine),
        recent_rhetorical_frames=ctx.recent_rhetorical_frames,
        recent_valence_modes=ctx.recent_valence_modes,
        semantic_focus_result=semantic_focus_result,
    )
    period_voice_copy = _apply_semantic_focus_preference(
        _render_period_voice_policy_slots(period_voice_policy),
        semantic_focus_result,
    )
    semantic_focus_guidance = _compose_semantic_focus_guidance(
        ctx,
        semantic_focus_result=semantic_focus_result,
    )

    opening_raw = track_story.get("period_opening") or _build_period_opening(ctx, spine, supports)
    policy_opening = _render_policy_opening(period_voice_policy)
    if semantic_focus_guidance.get("period_opening"):
        opening_raw = str(semantic_focus_guidance.get("period_opening") or "").strip()
        wrapped_opening = opening_raw
    else:
        if policy_opening:
            opening_raw = policy_opening
        wrapped_opening = _with_chapter_role_opening(opening_raw, spine)
    wrapped_opening = _remove_period_opening_tic(wrapped_opening)
    canonical_prefix = _build_canonical_promise_prefix(ctx.canonical_period_spine)
    promise_prefix = canonical_prefix or _build_promise_prefix(ctx.natal_promise, spine)
    big_picture = (
        str(semantic_focus_guidance.get("big_picture") or "").strip()
        or str(period_voice_copy.get("higher_meaning") or "").strip()
        or track_story.get("big_picture")
        or _build_big_picture(ctx, spine, supports)
    )
    mechanism = (
        str(semantic_focus_guidance.get("mechanism") or "").strip()
        or str(period_voice_copy.get("psychological_process") or "").strip()
        or _build_chain_paragraph(ctx, spine, supports)
    )
    growth_edge = (
        str(semantic_focus_guidance.get("growth_edge") or "").strip()
        or str(period_voice_copy.get("growth_edge") or "").strip()
        or track_story.get("growth_edge")
        or _build_growth_edge(ctx, spine, supports)
    )
    life_expression = (
        str(semantic_focus_guidance.get("relational_or_life_expression") or "").strip()
        or
        str(period_voice_copy.get("reason_line") or "").strip()
        or track_story.get("relational_or_life_expression")
        or _build_life_expression(ctx, spine, supports)
    )
    what_it_builds = (
        str(semantic_focus_guidance.get("what_it_builds") or "").strip()
        or
        str(period_voice_copy.get("what_it_builds") or "").strip()
        or track_story.get("what_it_builds")
        or _build_what_it_builds(ctx, spine, supports)
    )
    composer_plan = _compose_period_plan(
        ctx,
        semantic_focus_result=semantic_focus_result,
        semantic_focus_guidance=semantic_focus_guidance,
        promise_prefix=promise_prefix or "",
        opening_seed=wrapped_opening,
        big_picture_seed=big_picture,
        mechanism_seed=mechanism,
        growth_edge_seed=growth_edge,
        life_expression_seed=life_expression,
        what_it_builds_seed=what_it_builds,
    )
    period_reading_v1 = _build_period_reading_v1(composer_plan)
    legacy_fields = _legacy_fields_from_composer_plan(composer_plan)
    upper = legacy_fields["upper_meaning"]

    polished_fields = {
        key: _final_polish_tr(value)
        for key, value in legacy_fields.items()
        if key != "core_story"
    }
    polished_core_story = _final_polish_tr(str(period_reading_v1.get("full_text") or legacy_fields.get("core_story") or ""))
    render_guardrails = {
        name: _render_guardrail_issues(text)
        for name, text in polished_fields.items()
    }
    organic_guardrails = _render_period_reading_guardrails(period_reading_v1)

    return PeriodNarrative(
        period_reading_v1=period_reading_v1,
        period_opening=polished_fields["period_opening"],
        big_picture=polished_fields["big_picture"],
        mechanism=polished_fields["mechanism"],
        growth_edge=polished_fields["growth_edge"],
        relational_or_life_expression=polished_fields["relational_or_life_expression"],
        what_it_builds=polished_fields["what_it_builds"],
        upper_meaning=polished_fields["upper_meaning"],
        debug={
            "spine_event_id": str(spine.get("event_id") or ""),
            "support_event_ids": [str(e.get("event_id") or "") for e in supports],
            "track_id": track_id,
            "spine_role": _chapter_role_name(spine),
            "support_roles": [_chapter_role_name(event) for event in supports],
            "canonical_period_spine_source": str(((ctx.canonical_period_spine or {}) if isinstance(ctx.canonical_period_spine, Mapping) else {}).get("source") or ""),
            "canonical_period_spine_target_node_id": str(((ctx.canonical_period_spine or {}) if isinstance(ctx.canonical_period_spine, Mapping) else {}).get("target_node_id") or ""),
            "promise_prefix_source": "canonical_period_spine" if canonical_prefix else ("legacy_natal_promise" if promise_prefix else ""),
            "period_voice_policy_version": str(period_voice_policy.get("version") or ""),
            "period_voice_policy_reason_line_allowed": bool(period_voice_policy.get("reason_line_allowed")),
            "period_voice_policy_avoid_tags": list(period_voice_policy.get("avoid_tags") or []),
            "period_voice_policy_meaning_intent": str(period_voice_policy.get("meaning_intent") or ""),
            "period_voice_policy_rhetorical_frame": str(period_voice_policy.get("rhetorical_frame") or ""),
            "period_voice_policy_valence_mode": str(period_voice_policy.get("valence_mode") or ""),
            "period_voice_policy_intensity_mode": str(period_voice_policy.get("intensity_mode") or ""),
            "period_voice_policy_match_level": str(((period_voice_policy.get("debug") or {}) if isinstance(period_voice_policy.get("debug"), Mapping) else {}).get("match_level") or ""),
            "period_voice_policy_manifestation_context": dict(period_voice_policy.get("manifestation_context") or {}) if isinstance(period_voice_policy.get("manifestation_context"), Mapping) else {},
            "period_voice_policy": dict(period_voice_policy.get("debug") or {}) if isinstance(period_voice_policy.get("debug"), Mapping) else {},
            "semantic_focus": semantic_focus_debug,
            "semantic_focus_consumed": bool(semantic_focus_guidance.get("semantic_focus_consumed")),
            "semantic_focus_used_fields": list(semantic_focus_guidance.get("semantic_focus_used_fields") or []),
            "chapter_handoff_used_fields": list(semantic_focus_guidance.get("chapter_handoff_used_fields") or []),
            "suppressed_meanings_applied": list(semantic_focus_guidance.get("suppressed_meanings_applied") or []),
            "composer_mode": str(semantic_focus_guidance.get("composer_mode") or "legacy_fallback"),
            "chapter_priority": dict((ctx.period_core or {}).get("chapter_priority") or {})
            if isinstance((ctx.period_core or {}).get("chapter_priority"), Mapping)
            else {},
            "composer_plan": dict(composer_plan),
            "period_reading_v1_guardrails": organic_guardrails,
            "period_reading_v1_full_text": polished_core_story,
            "active_life_chapter_present": isinstance(ctx.active_life_chapter, Mapping) and bool(ctx.active_life_chapter),
            "active_life_chapter_type": str((ctx.active_life_chapter or {}).get("chapter_type") or "") if isinstance(ctx.active_life_chapter, Mapping) else "",
            "active_life_chapter_phase": str((ctx.active_life_chapter or {}).get("phase") or "") if isinstance(ctx.active_life_chapter, Mapping) else "",
            "active_life_chapter_selected_meaning": str((ctx.active_life_chapter or {}).get("selected_meaning") or "") if isinstance(ctx.active_life_chapter, Mapping) else "",
            "render_guardrails": render_guardrails,
        },
    )


def _render_period_voice_policy_slots(period_voice_policy: Mapping[str, Any] | None) -> Dict[str, str]:
    policy = period_voice_policy if isinstance(period_voice_policy, Mapping) else {}
    if not policy:
        return {}

    psychological_process = _render_policy_process(
        policy,
        _PERIOD_POLICY_SLOT_COPY.get(str(policy.get("psychological_process") or ""), ""),
    )
    higher_meaning = _render_policy_higher_meaning(
        policy,
        _PERIOD_POLICY_SLOT_COPY.get(str(policy.get("higher_meaning") or ""), ""),
    )
    growth_edge = _render_policy_growth_edge(
        policy,
        _PERIOD_POLICY_SLOT_COPY.get(str(policy.get("growth_edge") or ""), ""),
    )

    return {
        "psychological_process": psychological_process,
        "higher_meaning": higher_meaning,
        "growth_edge": growth_edge,
        "what_it_builds": _render_policy_build(
            policy,
            _PERIOD_POLICY_SLOT_COPY.get(str(policy.get("what_it_builds") or ""), ""),
        ),
        "reason_line": (
            _render_policy_reason_line(
                policy,
                _PERIOD_POLICY_SLOT_COPY.get(str(policy.get("reason_line_seed") or ""), ""),
            )
            if bool(policy.get("reason_line_allowed"))
            else ""
        ),
    }


def _apply_semantic_focus_preference(
    period_voice_copy: Mapping[str, Any] | None,
    semantic_focus_result: PeriodSemanticFocusResult | None,
) -> Dict[str, str]:
    out = dict(period_voice_copy or {})
    if not isinstance(semantic_focus_result, PeriodSemanticFocusResult):
        return out
    if semantic_focus_result.source == "unknown" or semantic_focus_result.confidence < 0.55:
        return out

    scene = semantic_focus_result.scene_translation_request or {}
    raw_meaning = str(semantic_focus_result.debug.get("raw_selected_meaning_text") or "").strip()
    if not str(out.get("higher_meaning") or "").strip() and raw_meaning:
        out["higher_meaning"] = raw_meaning

    if not str(out.get("psychological_process") or "").strip():
        human_scene = str(scene.get("human_scene") or "").strip()
        core_contrast = str(scene.get("core_contrast") or "").strip()
        if human_scene and core_contrast:
            out["psychological_process"] = f"{human_scene} içinde {core_contrast} daha görünür hale geliyor."
        elif human_scene:
            out["psychological_process"] = human_scene

    if not str(out.get("growth_edge") or "").strip():
        contrast = str(scene.get("shared_vs_private_contrast") or scene.get("core_contrast") or "").strip()
        if contrast:
            out["growth_edge"] = contrast

    if not str(out.get("reason_line") or "").strip():
        anchor = str(scene.get("chart_specific_anchor") or "").strip()
        if anchor:
            out["reason_line"] = anchor
    return out


def _ensure_semantic_focus_result(
    ctx: PeriodStoryContext,
    *,
    matched_events: Sequence[Mapping[str, Any]],
    chapter_role: str,
) -> PeriodSemanticFocusResult | None:
    if isinstance(ctx.semantic_focus_result, PeriodSemanticFocusResult):
        return ctx.semantic_focus_result
    if not (isinstance(ctx.active_life_chapter, Mapping) and bool(ctx.active_life_chapter)):
        return None

    policy_seed = build_period_voice_policy(
        canonical_period_spine=ctx.canonical_period_spine,
        matched_events=matched_events,
        chapter_role=chapter_role,
        canonical_backing_node_ids=_canonical_backing_node_ids(ctx.canonical_period_spine),
        recent_rhetorical_frames=ctx.recent_rhetorical_frames,
        recent_valence_modes=ctx.recent_valence_modes,
        semantic_focus_result=None,
    )
    return resolve_period_semantic_focus(
        canonical_period_spine=ctx.canonical_period_spine,
        active_life_chapter=ctx.active_life_chapter,
        period_voice_policy=policy_seed,
        manifestation_context=policy_seed.get("manifestation_context")
        if isinstance(policy_seed.get("manifestation_context"), Mapping)
        else None,
        selected_events=matched_events,
        period_core_seed=ctx.period_core,
        canonical_natal_state=ctx.chart_snapshot,
        debug=True,
    )


def _compose_semantic_focus_guidance(
    ctx: PeriodStoryContext,
    *,
    semantic_focus_result: PeriodSemanticFocusResult | None,
) -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "semantic_focus_consumed": False,
        "semantic_focus_used_fields": [],
        "chapter_handoff_used_fields": [],
        "suppressed_meanings_applied": [],
        "composer_mode": "legacy_fallback",
    }
    if not isinstance(semantic_focus_result, PeriodSemanticFocusResult):
        return payload
    if semantic_focus_result.source == "unknown" or semantic_focus_result.confidence < 0.55:
        return payload

    chapter = dict(ctx.active_life_chapter or {}) if isinstance(ctx.active_life_chapter, Mapping) else {}
    semantic_focus = dict(chapter.get("semantic_focus") or {}) if isinstance(chapter.get("semantic_focus"), Mapping) else {}
    handoff = dict(chapter.get("renderer_handoff") or {}) if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    scene = dict(semantic_focus_result.scene_translation_request or {})
    source = str(semantic_focus_result.source or "").strip()
    raw_meaning_text = str(
        semantic_focus_result.debug.get("raw_selected_meaning_text")
        or chapter.get("selected_meaning")
        or ""
    ).strip()
    meaning_key = str(semantic_focus_result.selected_meaning or "").strip()
    meaning_family = str(semantic_focus_result.meaning_family or semantic_focus_result.debug.get("selected_meaning_family") or "").strip()
    human_scene = str(handoff.get("human_scene") or scene.get("human_scene") or "").strip()
    core_contrast = str(handoff.get("core_contrast") or scene.get("core_contrast") or "").strip()
    chart_anchor = str(handoff.get("chart_specific_anchor") or scene.get("chart_specific_anchor") or "").strip()
    suppressed = _dedupe_tokens(
        list(semantic_focus_result.suppressed_meanings)
        + list(semantic_focus.get("not_this") or [])
        + [str(item.get("reading") or "").strip() for item in (chapter.get("suppressed_surface_readings") or []) if isinstance(item, Mapping)]
        + [str(item.get("reading") or "").strip() for item in (chapter.get("suppressed_readings") or []) if isinstance(item, Mapping)]
    )

    fields = _compose_guided_fields(
        source=source,
        meaning_key=meaning_key,
        meaning_family=meaning_family,
        raw_meaning_text=raw_meaning_text,
        human_scene=human_scene,
        core_contrast=core_contrast,
        chart_anchor=chart_anchor,
    )
    payload["semantic_focus_consumed"] = True
    payload["composer_mode"] = "semantic_focus_guided"
    payload["suppressed_meanings_applied"] = suppressed
    payload["semantic_focus_used_fields"] = _dedupe_tokens(
        [
            "selected_meaning" if meaning_key else "",
            "meaning_family" if meaning_family else "",
            "scene_translation_request" if scene else "",
            "suppressed_meanings" if suppressed else "",
            "raw_selected_meaning_text" if raw_meaning_text else "",
        ]
    )
    payload["chapter_handoff_used_fields"] = _dedupe_tokens(
        [
            "renderer_handoff.human_scene" if human_scene else "",
            "renderer_handoff.core_contrast" if core_contrast else "",
            "renderer_handoff.chart_specific_anchor" if chart_anchor else "",
            "selected_meaning" if raw_meaning_text else "",
        ]
    )
    if any(str(fields.get(key) or "").strip() for key in ("period_opening", "mechanism", "growth_edge", "what_it_builds", "relational_or_life_expression", "big_picture")):
        payload.update(fields)
    return payload


def _compose_guided_fields(
    *,
    source: str,
    meaning_key: str,
    meaning_family: str,
    raw_meaning_text: str,
    human_scene: str,
    core_contrast: str,
    chart_anchor: str,
) -> Dict[str, str]:
    if source != "life_chapter":
        return {}
    if meaning_key == "speech_authority" or "speech_authority" in meaning_family:
        return {
            "period_opening": (
                "Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında "
                "sözünün ağırlığı değişiyor. Hızlı tepkiyle gerçekten nerede durduğunu söylemek artık aynı şey değil."
            ),
            "big_picture": raw_meaning_text,
            "mechanism": (
                "Bu en çok kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında görünür. "
                "Eskiden refleksle çıkan söz, şimdi daha seçilmiş bir ağırlık ve daha sahipli bir duruş istiyor."
            ),
            "growth_edge": (
                "İlk cevabı son söz gibi kullanmak yerine, ne söyleyeceğini ve hangi cümlenin gerçekten sana ait olduğunu seçebilmek."
            ),
            "what_it_builds": "Daha seçilmiş, daha sahipli ve daha sorumlu bir konuşma biçimi.",
            "relational_or_life_expression": (
                "Günlük konuşmalarda ve küçük cevaplarda bile hızın yerini daha bilinçli bir ifade almaya başlar."
            ),
        }
    if meaning_key == "shared_emotional_territory" or "shared_trust" in meaning_family:
        return {
            "period_opening": (
                "Mahrem konuşmalarda, birlikte taşınan yüklerde ve sessiz duygusal borçlarda "
                "neyin ortak, neyin tek başına taşındığı daha belirgin oluyor."
            ),
            "big_picture": raw_meaning_text,
            "mechanism": (
                "Bu en çok mahrem konuşmalar, birlikte taşınan yükler ve sessiz sorumluluk anlarında görünür. "
                "İçeride tek başına tutulan ağırlık, şimdi güvenin ve paylaşılmış yükün adını istemeye başlıyor."
            ),
            "growth_edge": (
                "Her şeyi içeride tek başına taşımak yerine, hangi yükün paylaşılacağını ve hangi sınırın sana ait olduğunu söyleyebilmek."
            ),
            "what_it_builds": "Paylaşılan güveni ve özel ağırlığı aynı cümlede tutabilen daha dayanıklı bir yakınlık.",
            "relational_or_life_expression": (
                "Yakınlık burada sadece açılmak değil; neyin birlikte taşındığını, neyin sana ait kaldığını söyleyebilmek."
            ),
        }
    if meaning_key == "directional_self_definition" or "nodal_direction" in meaning_family:
        return {
            "period_opening": (
                "Yan yana dururken kendi sözünü nasıl ayarladığın değişiyor. "
                "İlişkiyi korumak için kendini kısmakla yönünü daha doğrudan söylemek artık aynı yerde durmuyor."
            ),
            "big_picture": raw_meaning_text,
            "mechanism": (
                "Bu en çok yan yana durduğun anlarda, kısa konuşmalarda ve yön seçimi gereken yerlerde görünür. "
                "Eskiden başkasına göre ayar veren refleks, şimdi daha doğrudan bir yön duygusu istiyor."
            ),
            "growth_edge": (
                "Onayı korumak için yönünü yumuşatmak yerine, ilişkiyi silmeden daha doğrudan konuşabilmek."
            ),
            "what_it_builds": "Onay arayışına çökmeyen daha doğrudan bir yön duygusu.",
            "relational_or_life_expression": (
                "Küçük konuşmalarda bile kendi yönünü cümlenin içinde tutmak daha mümkün hale gelir."
            ),
        }

    opening_parts = []
    if human_scene:
        opening_parts.append(f"{_capitalize_first(human_scene)} daha görünür hale geliyor.")
    if core_contrast:
        opening_parts.append(f"{_capitalize_first(core_contrast)} artık aynı cümlede durmuyor.")
    opening = " ".join(opening_parts).strip()
    mechanism = ""
    if human_scene and core_contrast:
        mechanism = f"Bu en çok {human_scene} içinde görünür. Eskiden sessiz kalan fark, şimdi {core_contrast} diye adını istemeye başlıyor."
    elif chart_anchor:
        mechanism = f"Bu en çok gündelik hayatın küçük anlarında görünür. Dışarıdan küçük duran şey, içeride {chart_anchor} meselesine bağlanır."
    growth = core_contrast or "Neyi otomatik yaptığını fark edip daha sahipli bir seçim yapabilmek."
    builds = chart_anchor or raw_meaning_text or "Daha sahipli bir yön duygusu."
    life = human_scene or ""
    return {
        "period_opening": opening,
        "big_picture": raw_meaning_text,
        "mechanism": mechanism,
        "growth_edge": growth,
        "what_it_builds": builds,
        "relational_or_life_expression": life,
    }


def _compose_period_plan(
    ctx: PeriodStoryContext,
    *,
    semantic_focus_result: PeriodSemanticFocusResult | None,
    semantic_focus_guidance: Mapping[str, Any],
    promise_prefix: str,
    opening_seed: str,
    big_picture_seed: str,
    mechanism_seed: str,
    growth_edge_seed: str,
    life_expression_seed: str,
    what_it_builds_seed: str,
) -> Dict[str, str]:
    if isinstance(semantic_focus_result, PeriodSemanticFocusResult) and semantic_focus_guidance.get("semantic_focus_consumed"):
        guided_plan = _guided_composer_plan(
            ctx=ctx,
            semantic_focus_result=semantic_focus_result,
            promise_prefix=promise_prefix,
            opening_seed=opening_seed,
            big_picture_seed=big_picture_seed,
            mechanism_seed=mechanism_seed,
            growth_edge_seed=growth_edge_seed,
            life_expression_seed=life_expression_seed,
            what_it_builds_seed=what_it_builds_seed,
        )
        if guided_plan:
            return guided_plan

    return _fallback_composer_plan(
        promise_prefix=promise_prefix,
        opening_seed=opening_seed,
        big_picture_seed=big_picture_seed,
        mechanism_seed=mechanism_seed,
        growth_edge_seed=growth_edge_seed,
        life_expression_seed=life_expression_seed,
        what_it_builds_seed=what_it_builds_seed,
    )


def _guided_composer_plan(
    *,
    ctx: PeriodStoryContext,
    semantic_focus_result: PeriodSemanticFocusResult,
    promise_prefix: str,
    opening_seed: str,
    big_picture_seed: str,
    mechanism_seed: str,
    growth_edge_seed: str,
    life_expression_seed: str,
    what_it_builds_seed: str,
) -> Dict[str, str]:
    chapter = dict(ctx.active_life_chapter or {}) if isinstance(ctx.active_life_chapter, Mapping) else {}
    handoff = dict(chapter.get("renderer_handoff") or {}) if isinstance(chapter.get("renderer_handoff"), Mapping) else {}
    scene = dict(semantic_focus_result.scene_translation_request or {})
    meaning_key = str(semantic_focus_result.selected_meaning or "").strip()
    meaning_family = str(
        semantic_focus_result.meaning_family
        or semantic_focus_result.debug.get("selected_meaning_family")
        or ""
    ).strip()
    raw_meaning_text = str(
        semantic_focus_result.debug.get("raw_selected_meaning_text")
        or chapter.get("selected_meaning")
        or ""
    ).strip()
    human_scene = str(handoff.get("human_scene") or scene.get("human_scene") or "").strip()
    core_contrast = str(handoff.get("core_contrast") or scene.get("core_contrast") or "").strip()
    chart_anchor = str(handoff.get("chart_specific_anchor") or scene.get("chart_specific_anchor") or "").strip()
    source = str(semantic_focus_result.source or "").strip()

    if source == "life_chapter" and (meaning_key == "speech_authority" or "speech_authority" in meaning_family):
        return {
            "hook": "Kısa mesajlarda, yarım kalmış konuşmalarda ve hızlı cevap verme anlarında sözünün ağırlığı değişiyor.",
            "scene_anchor": "",
            "core_contrast": "Eskiden refleksle çıkan cümle seni hemen konumlandırıyor gibi gelebilirdi.",
            "mechanism": "Şimdi ilk tepkiyi son söz yapmak yerine, hangi cümlenin gerçekten sana ait olduğunu seçiyorsun.",
            "growth_edge": "İlk cevabı son söz gibi kullanmak yerine, ne söyleyeceğini ve hangi cümlenin gerçekten sana ait olduğunu seçebilmek.",
            "what_it_builds": "Daha sahipli ve daha sorumlu bir konuşma biçimi.",
            "closer": "Bu dönem sana daha çok konuşmayı değil, sözünü daha sahipli kurmayı öğretiyor.",
            "legacy_prefix": promise_prefix,
            "semantic_mode": "guided",
        }
    if source == "life_chapter" and (meaning_key == "shared_emotional_territory" or "shared_trust" in meaning_family):
        return {
            "hook": "Mahrem konuşmalarda ve birlikte taşınan yüklerde neyin ortak, neyin tek başına kaldığı daha görünür oluyor.",
            "scene_anchor": "",
            "core_contrast": "Bazı şeyleri içeride tutmak seni güvende hissettirmiş olabilir.",
            "mechanism": "Ama güvenin sadece susarak değil, neyi paylaşacağını ve hangi sınırın sana ait olduğunu söyleyerek de kurulabileceğini görüyorsun.",
            "growth_edge": "Her şeyi içeride tek başına taşımak yerine, hangi yükün paylaşılacağını ve hangi sınırın sana ait olduğunu söyleyebilmek.",
            "what_it_builds": "Paylaşılan güveni ve özel ağırlığı aynı cümlede tutabilen daha dayanıklı bir yakınlık.",
            "closer": "Bu sana hem paylaşılanı taşıyan hem özel alanı koruyan daha dayanıklı bir yakınlık kurduruyor.",
            "legacy_prefix": promise_prefix,
            "semantic_mode": "guided",
        }
    if source == "life_chapter" and (meaning_key == "directional_self_definition" or "nodal_direction" in meaning_family):
        return {
            "hook": "Yan yana dururken kendi sözünü ne kadar ayarladığını daha net fark ediyorsun.",
            "scene_anchor": "",
            "core_contrast": "İlişkiyi korumak için kendini kısmana gerek kalmadan, yönünü daha açık söylemeyi öğreniyorsun.",
            "mechanism": "Bu kopmak değil; onayın içinde erimeden kendi çizgini de masada tutmak.",
            "growth_edge": "Onayı korumak için yönünü yumuşatmak yerine, ilişkiyi silmeden daha doğrudan konuşabilmek.",
            "what_it_builds": "Onay arayışına çökmeyen daha doğrudan bir yön duygusu.",
            "closer": "Bu dönem sende onay arayışına çökmeyen daha doğrudan bir yön duygusu kuruyor.",
            "legacy_prefix": promise_prefix,
            "semantic_mode": "guided",
        }

    return _semantic_enriched_fallback_plan(
        semantic_focus_result=semantic_focus_result,
        promise_prefix=promise_prefix,
        opening_seed=opening_seed,
        big_picture_seed=big_picture_seed,
        mechanism_seed=mechanism_seed,
        growth_edge_seed=growth_edge_seed,
        life_expression_seed=life_expression_seed,
        what_it_builds_seed=what_it_builds_seed,
        featured_events=[
            event
            for event in ((ctx.period_core or {}).get("featured_events") or [])
            if isinstance(event, Mapping)
        ],
        human_scene=human_scene,
        core_contrast=core_contrast,
        chart_anchor=chart_anchor,
        raw_meaning_text=raw_meaning_text,
    )


_FALLBACK_SCAFFOLD_PHRASES: tuple[str, ...] = (
    "Burada daha yavaş ama daha kalıcı bir çizgi oluşuyor",
    "Bu dönem hayatının bir alanı daha görünür hale geliyor",
    # Softened variant emitted by _soften_organic_fallback_text after the
    # "Bu dönem" prefix is stripped — still scaffold, still abstract.
    "Hayatının bir alanı daha görünür hale geliyor",
    "İlk bakışta görünen şey tek mesele değil",
    "Sende zaten çalışan birkaç ayrı taraf var",
    "Bu tema küçük cümlelerin ağırlığı içinden büyüyor",
    "Bu konu boşuna buradan açılmıyor",
    "küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir",
    # Wave-2 additions: "onlar" without referent + interchangeable closer.
    "Bu dönem onlar birbirini daha çok duyuyor",
    "Daha esnek ama dağılmayan bir yön duygusu kuruyorsun",
)


def _strip_fallback_scaffold_sentences(text: str) -> str:
    """Drop generic non-LifeChapter scaffold sentences from fallback prose.

    Targets short, interchangeable sentences that recur across cases without
    carrying chart-specific signal. Operates per-sentence so we never mangle
    well-formed surrounding prose.
    """
    if not text:
        return ""
    sentences = _split_sentences(text)
    kept: list[str] = []
    for sentence in sentences:
        probe = sentence.lower()
        if any(phrase.lower() in probe for phrase in _FALLBACK_SCAFFOLD_PHRASES):
            continue
        kept.append(sentence)
    return " ".join(kept).strip()


# House-anchored opening scenes for non-LifeChapter fallback.
# Used to anchor the opening on the natal-side house (or a primary identity-axis
# secondary domain) instead of a transit-side surface scene.
_FALLBACK_HOUSE_OPENINGS: dict[int, str] = {
    1: "Kimliğinin ve duruşunun çizgisi bu dönem daha fazla görünür oluyor.",
    2: "Değer gördüğün ve özdeğer kurduğun alan bu dönem daha fazla görünür oluyor.",
    3: "Yakın çevrendeki ses ve gündelik konuşmaların ağırlığı bu dönem daha fazla görünür oluyor.",
    4: (
        "Sana ait hissettiren alan bu dönem daha fazla görünür oluyor. "
        "Ev, iç güvenlik ya da yalnız kaldığında kurduğun düzen sadece arka plan gibi kalmıyor; "
        "kimliğini ve sınırını da etkiliyor."
    ),
    5: "Kendini yaratıcı biçimde gösterdiğin alan bu dönem daha fazla görünür oluyor.",
    6: "Günlük ritmin ve sürdürülebilirliğin bu dönem daha fazla görünür oluyor.",
    7: "İlişkilerde kurduğun denge ve karşılıklı alan bu dönem daha fazla görünür oluyor.",
    8: "Derin bağ ve ortak alanlardaki paylaşım bu dönem daha fazla görünür oluyor.",
    9: "Hayata verdiğin anlam ve büyük resmin bu dönem daha fazla görünür oluyor.",
    10: "Dış dünyadaki rolün ve görünür duruşun bu dönem daha fazla görünür oluyor.",
    11: "Geleceğe doğru kurduğun çevre ve ait olduğun topluluklar bu dönem daha fazla görünür oluyor.",
    12: "İç dünyana çekildiğin alan ve çözülüşün bu dönem daha fazla görünür oluyor.",
}

_IDENTITY_AXIS_HOUSES = (1, 4, 7, 10)


def _resolve_primary_anchor_house(
    *,
    scene_request: Mapping[str, Any],
    secondary_domains: Sequence[Any],
    featured_events: Sequence[Mapping[str, Any]],
) -> int | None:
    """Pick a natal-side house to anchor the fallback opening on.

    Order of preference:
    1. ``house_4`` if it appears in ``secondary_domains`` — inner-foundation
       anchor consistently outperforms the visible-identity anchor in
       fallback prose (the visible axis can ride along inside the same
       sentence). Mirrors the manifestation_context_v1 "sana ait hissettiren
       alan" framing.
    2. ``scene_request.target_planet_house`` — natal point's house.
    3. Other identity-axis houses (1, 7, 10) in ``secondary_domains``.
    4. ``natal_point_house`` of the strongest featured event.
    """
    secondary_houses: list[int] = []
    for entry in secondary_domains or ():
        token = str(entry or "").strip().lower()
        if not token.startswith("house_"):
            continue
        try:
            house_num = int(token.split("_", 1)[1])
        except (ValueError, IndexError):
            continue
        if 1 <= house_num <= 12:
            secondary_houses.append(house_num)

    if 4 in secondary_houses:
        return 4

    candidate = scene_request.get("target_planet_house") if isinstance(scene_request, Mapping) else None
    if isinstance(candidate, int) and 1 <= candidate <= 12:
        return candidate

    for house_num in secondary_houses:
        if house_num in _IDENTITY_AXIS_HOUSES:
            return house_num

    for event in featured_events or ():
        if not isinstance(event, Mapping):
            continue
        houses = event.get("houses")
        if isinstance(houses, Mapping):
            natal_house = houses.get("natal_point_house")
            if isinstance(natal_house, int) and 1 <= natal_house <= 12:
                return natal_house
    return None


def _fallback_primary_anchor_sentence(
    *,
    scene_request: Mapping[str, Any],
    secondary_domains: Sequence[Any],
    featured_events: Sequence[Mapping[str, Any]],
    life_scene: str,
) -> str:
    """Build a primary-domain anchor sentence for fallback opening.

    Falls back to the supplied ``life_scene`` only when no identifiable
    natal-side house is available.
    """
    house = _resolve_primary_anchor_house(
        scene_request=scene_request,
        secondary_domains=secondary_domains,
        featured_events=featured_events,
    )
    if house is not None:
        return _FALLBACK_HOUSE_OPENINGS.get(house, "")
    return _direct_scene_sentence("", life_scene)


def _h4_inner_combo_has_visible_axis(
    *,
    scene_request: Mapping[str, Any],
    featured_events: Sequence[Mapping[str, Any]],
) -> bool:
    target_planet_house = (
        scene_request.get("target_planet_house") if isinstance(scene_request, Mapping) else None
    )
    if target_planet_house in {1, 7, 10}:
        return True
    for event in featured_events or ():
        if not isinstance(event, Mapping):
            continue
        houses = event.get("houses")
        if not isinstance(houses, Mapping):
            continue
        np_house = houses.get("natal_point_house")
        if isinstance(np_house, int) and np_house in {1, 7, 10}:
            return True
    return False


def _fallback_chart_specific_mechanism_support(
    *,
    scene_request: Mapping[str, Any],
    secondary_domains: Sequence[Any],
    featured_events: Sequence[Mapping[str, Any]],
) -> str:
    """Concrete h4-inner / visible-axis dynamic line.

    Replaces the stripped "Bu dönem onlar birbirini daha çok duyuyor" slot
    with a felt-sense sentence when the h4 inner-foundation anchor leads and
    a visible-axis natal point (h1/7/10) is in the picture. Returns "" when
    no opinionated combo is detected.
    """
    house = _resolve_primary_anchor_house(
        scene_request=scene_request,
        secondary_domains=secondary_domains,
        featured_events=featured_events,
    )
    if house != 4:
        return ""
    if not _h4_inner_combo_has_visible_axis(
        scene_request=scene_request,
        featured_events=featured_events,
    ):
        return ""
    return (
        "Evde ya da yalnız kaldığında taşıdığın duygu, dışarıdaki "
        "duruşuna daha kolay yansıyor."
    )


def _fallback_chart_specific_closer(
    *,
    scene_request: Mapping[str, Any],
    secondary_domains: Sequence[Any],
    featured_events: Sequence[Mapping[str, Any]],
) -> str:
    """Pick a closer that reflects the natal-side anchor combo.

    When the inner-foundation (h4) anchor leads and the visible-axis
    (h1/7/10) is also in the picture, return a composite "inside <-> outside"
    closer instead of the generic "Daha esnek ama dağılmayan…" line. Returns
    "" when no opinionated combo is detected — caller should keep the
    seed-derived closer in that case.
    """
    house = _resolve_primary_anchor_house(
        scene_request=scene_request,
        secondary_domains=secondary_domains,
        featured_events=featured_events,
    )
    if house != 4:
        return ""

    if _h4_inner_combo_has_visible_axis(
        scene_request=scene_request,
        featured_events=featured_events,
    ):
        return (
            "Bu sana içeride hissettiğin şeyle dışarıda gösterdiğin "
            "duruşu aynı hatta toplamayı öğretiyor."
        )
    return (
        "Bu sana neyin gerçekten sana ait olduğunu daha sakin ayırmayı "
        "öğretiyor."
    )


def _semantic_enriched_fallback_plan(
    *,
    semantic_focus_result: PeriodSemanticFocusResult,
    promise_prefix: str,
    opening_seed: str,
    big_picture_seed: str,
    mechanism_seed: str,
    growth_edge_seed: str,
    life_expression_seed: str,
    what_it_builds_seed: str,
    featured_events: Sequence[Mapping[str, Any]],
    human_scene: str,
    core_contrast: str,
    chart_anchor: str,
    raw_meaning_text: str,
) -> Dict[str, str]:
    plan = _fallback_composer_plan(
        promise_prefix=promise_prefix,
        opening_seed=opening_seed,
        big_picture_seed=big_picture_seed,
        mechanism_seed=mechanism_seed,
        growth_edge_seed=growth_edge_seed,
        life_expression_seed=life_expression_seed,
        what_it_builds_seed=what_it_builds_seed,
    )

    scene_request = (
        dict(semantic_focus_result.scene_translation_request or {})
        if isinstance(semantic_focus_result.scene_translation_request, Mapping)
        else {}
    )
    secondary_domains = list(getattr(semantic_focus_result, "secondary_domains", []) or [])
    scene_seed = str(scene_request.get("context_seed") or "").strip()
    life_scene = str(scene_request.get("life_scene") or human_scene or "").strip()
    focus_hint = str(core_contrast or raw_meaning_text or "").strip()
    chart_hint = str(chart_anchor or "").strip()
    evidence_hint = _period_featured_event_evidence_bridge(featured_events)

    # Strip generic scaffold sentences from softened seeds before we layer in
    # primary-domain anchor / scene-as-support text.
    for key in ("hook", "core_contrast", "mechanism", "growth_edge", "what_it_builds", "closer"):
        plan[key] = _strip_fallback_scaffold_sentences(str(plan.get(key) or ""))

    primary_anchor = _fallback_primary_anchor_sentence(
        scene_request=scene_request,
        secondary_domains=secondary_domains,
        featured_events=featured_events,
        life_scene=life_scene,
    )

    if primary_anchor:
        # Primary domain leads. The transit-side scene becomes support.
        anchor_sentence = _ensure_sentence(primary_anchor)
        existing_hook = str(plan.get("hook") or "").strip()
        if anchor_sentence.lower() not in existing_hook.lower():
            plan["hook"] = (
                anchor_sentence
                if not existing_hook
                else _join_parts(anchor_sentence, existing_hook)
            )
        plan["scene_anchor"] = ""

        # Evidence-first mechanism with optional chart-specific lead:
        # 1. concrete h4+visible-axis felt-sense lead (when applicable)
        # 2. featured-event evidence summary (raw, chart-specific)
        # 3. transit-side scene support
        # 4. any remaining softened seed text (after scaffold strip)
        # This avoids "Bu dönem onlar…" / "Sende zaten çalışan…" leading
        # the second block and replaces them with a concrete felt-sense
        # sentence when the chart shape supports it.
        seed_mechanism = str(plan.get("mechanism") or "").strip()
        rebuilt_mechanism = ""
        chart_specific_lead = _fallback_chart_specific_mechanism_support(
            scene_request=scene_request,
            secondary_domains=secondary_domains,
            featured_events=featured_events,
        )
        if chart_specific_lead:
            rebuilt_mechanism = _ensure_sentence(chart_specific_lead)
        if evidence_hint:
            rebuilt_mechanism = _append_sentence_if_missing(
                rebuilt_mechanism, evidence_hint
            )
        scene_support = _direct_scene_sentence(scene_seed, life_scene)
        if scene_support:
            scene_support_sentence = _ensure_sentence(scene_support)
            if scene_support_sentence.lower() not in plan["hook"].lower():
                rebuilt_mechanism = _append_sentence_if_missing(
                    rebuilt_mechanism, scene_support_sentence
                )
        if seed_mechanism:
            rebuilt_mechanism = _append_sentence_if_missing(
                rebuilt_mechanism, seed_mechanism
            )
        plan["mechanism"] = rebuilt_mechanism

        # Chart-specific closer override when h4 inner anchor pairs with a
        # visible-axis (h1/7/10) natal point. Replaces the generic
        # "Daha esnek ama dağılmayan…" closer (which is now scaffold-stripped
        # from the seed path anyway).
        chart_specific_closer = _fallback_chart_specific_closer(
            scene_request=scene_request,
            secondary_domains=secondary_domains,
            featured_events=featured_events,
        )
        if chart_specific_closer:
            plan["closer"] = _ensure_sentence(chart_specific_closer)
    else:
        # No natal-side anchor; keep prior scene-led opening behavior.
        hook_scene = _direct_scene_sentence(scene_seed, life_scene)
        if hook_scene:
            hook_sentence = _ensure_sentence(hook_scene)
            hook_text = str(plan.get("hook") or "").strip()
            if life_scene and life_scene.lower() not in hook_text.lower():
                plan["hook"] = _join_parts(hook_sentence, hook_text)
            elif hook_sentence.lower() not in hook_text.lower():
                plan["hook"] = _join_parts(hook_sentence, hook_text)

        scene_anchor = _direct_scene_sentence(scene_seed, life_scene)
        if scene_anchor:
            scene_sentence = _ensure_sentence(scene_anchor)
            plan["scene_anchor"] = (
                ""
                if scene_sentence.lower() in str(plan.get("hook") or "").lower()
                else scene_sentence
            )

        if chart_hint:
            plan["mechanism"] = _append_sentence_if_missing(plan.get("mechanism"), chart_hint)
        if evidence_hint:
            plan["mechanism"] = _append_sentence_if_missing(plan.get("mechanism"), evidence_hint)

    if focus_hint:
        plan["core_contrast"] = _append_sentence_if_missing(plan.get("core_contrast"), focus_hint)

    if primary_anchor and chart_hint:
        plan["mechanism"] = _append_sentence_if_missing(plan.get("mechanism"), chart_hint)

    plan["semantic_mode"] = "guided_fallback"
    return plan


def _fallback_composer_plan(
    *,
    promise_prefix: str,
    opening_seed: str,
    big_picture_seed: str,
    mechanism_seed: str,
    growth_edge_seed: str,
    life_expression_seed: str,
    what_it_builds_seed: str,
) -> Dict[str, str]:
    hook = _ensure_sentence(_soften_organic_fallback_text(_strip_prefix_if_present(opening_seed, promise_prefix), role="hook"))
    unfolding_a = _ensure_sentence(_soften_organic_fallback_text(big_picture_seed, role="unfolding"))
    unfolding_b = _ensure_sentence(_soften_organic_fallback_text(mechanism_seed, role="mechanism"))
    growth = _ensure_sentence(_soften_organic_fallback_text(growth_edge_seed, role="growth"))
    builds = _ensure_sentence(_soften_organic_fallback_text(what_it_builds_seed, role="builds"))
    closer = _ensure_sentence(_soften_organic_fallback_text(life_expression_seed or what_it_builds_seed, role="closer"))
    return {
        "hook": hook,
        "scene_anchor": "",
        "core_contrast": unfolding_a,
        "mechanism": unfolding_b,
        "growth_edge": growth,
        "what_it_builds": builds,
        "closer": closer,
        "legacy_prefix": promise_prefix,
        "semantic_mode": "fallback",
    }


def _append_sentence_if_missing(base: Any, extra: Any) -> str:
    base_text = str(base or "").strip()
    extra_text = str(extra or "").strip()
    if not extra_text:
        return base_text
    sentence = _ensure_sentence(extra_text)
    if not base_text:
        return sentence
    if sentence.lower() in base_text.lower() or extra_text.lower() in base_text.lower():
        return base_text
    return _join_parts(base_text, sentence)


def _period_featured_event_evidence_bridge(
    featured_events: Sequence[Mapping[str, Any]],
) -> str:
    if not featured_events:
        return ""

    candidates: List[str] = []
    seen: set[str] = set()
    first = featured_events[0] if featured_events else {}
    if isinstance(first, Mapping):
        interpretation = first.get("interpretation") if isinstance(first.get("interpretation"), Mapping) else {}
        for value in (
            interpretation.get("summary"),
            interpretation.get("where"),
            interpretation.get("headline"),
        ):
            probe = " ".join(_normalized_tokens(str(value or "")))
            if probe:
                seen.add(probe)
                candidates.append(str(value or "").strip())
                break

    for event in featured_events[1:3]:
        if not isinstance(event, Mapping):
            continue
        interpretation = event.get("interpretation") if isinstance(event.get("interpretation"), Mapping) else {}
        for value in (
            interpretation.get("where"),
            interpretation.get("summary"),
            interpretation.get("headline"),
        ):
            text = str(value or "").strip()
            probe = " ".join(_normalized_tokens(text))
            if not probe or probe in seen:
                continue
            seen.add(probe)
            candidates.append(text)
            break
        if len(candidates) >= 2:
            break

    joined = " ".join(candidate for candidate in candidates if candidate)
    return joined.strip()


def _build_period_reading_v1(composer_plan: Mapping[str, Any]) -> Dict[str, Any]:
    hook_block = _join_parts(
        str(composer_plan.get("hook") or "").strip(),
        str(composer_plan.get("scene_anchor") or "").strip(),
    )
    unfolding_block = _join_parts(
        str(composer_plan.get("core_contrast") or "").strip(),
        str(composer_plan.get("mechanism") or "").strip(),
    )
    growth_seed = _join_parts(
        str(composer_plan.get("growth_edge") or "").strip(),
        str(composer_plan.get("what_it_builds") or "").strip(),
    )
    closer = str(composer_plan.get("closer") or "").strip()
    semantic_mode = str(composer_plan.get("semantic_mode") or "").strip()

    blocks: List[Dict[str, str]] = []
    if hook_block:
        blocks.append({"role": "hook", "text": hook_block})
    if unfolding_block:
        blocks.append({"role": "unfolding", "text": unfolding_block})
    if semantic_mode == "guided" and closer:
        growth_text = closer
    else:
        growth_text = growth_seed or closer
    if growth_text:
        blocks.append({"role": "growth", "text": growth_text})
    if semantic_mode != "guided" and closer and growth_text != closer:
        blocks.append({"role": "closer", "text": closer})

    blocks = [block for block in blocks if str(block.get("text") or "").strip()]
    if len(blocks) > 4:
        blocks = blocks[:4]
    if len(blocks) < 3:
        extras = [
            ("growth", growth_seed),
            ("closer", closer),
        ]
        for role, text in extras:
            if len(blocks) >= 3:
                break
            cleaned = str(text or "").strip()
            if cleaned and all(existing["text"] != cleaned for existing in blocks):
                blocks.append({"role": role, "text": cleaned})
    if len(blocks) > 4:
        blocks = blocks[:4]

    seen_sentences: set[str] = set()
    normalized_blocks: List[Dict[str, str]] = []
    for block in blocks:
        text = str(block.get("text") or "").strip()
        if not text:
            continue
        polished = _polish_period_block_text(text, seen_sentences=seen_sentences)
        if not polished:
            continue
        normalized_blocks.append(
            {
                "role": str(block.get("role") or "").strip(),
                "text": polished,
            }
        )
    full_text = "\n\n".join(block["text"] for block in normalized_blocks)
    return {
        "version": "period_reading_v1",
        "blocks": normalized_blocks,
        "full_text": full_text,
    }


def _legacy_fields_from_composer_plan(composer_plan: Mapping[str, Any]) -> Dict[str, str]:
    prefix = str(composer_plan.get("legacy_prefix") or "").strip()
    hook = _final_polish_tr(str(composer_plan.get("hook") or "").strip())
    scene_anchor = _final_polish_tr(str(composer_plan.get("scene_anchor") or "").strip())
    core_contrast = _final_polish_tr(str(composer_plan.get("core_contrast") or "").strip())
    mechanism = _final_polish_tr(str(composer_plan.get("mechanism") or "").strip())
    growth_edge = _final_polish_tr(str(composer_plan.get("growth_edge") or "").strip())
    what_it_builds = _final_polish_tr(str(composer_plan.get("what_it_builds") or "").strip())
    closer = _final_polish_tr(str(composer_plan.get("closer") or "").strip())
    opening = _join_parts(prefix, hook)
    big_picture = _join_parts(core_contrast, mechanism)
    relational = closer or scene_anchor or what_it_builds
    upper = what_it_builds or closer
    return {
        "period_opening": opening,
        "big_picture": big_picture,
        "mechanism": mechanism or big_picture,
        "growth_edge": growth_edge or what_it_builds,
        "relational_or_life_expression": relational,
        "what_it_builds": what_it_builds or closer,
        "upper_meaning": upper,
        "core_story": "\n\n".join(
            part
            for part in (hook, big_picture, relational)
            if str(part).strip()
        ),
    }


def _render_period_reading_guardrails(period_reading_v1: Mapping[str, Any]) -> Dict[str, Any]:
    blocks = period_reading_v1.get("blocks") if isinstance(period_reading_v1.get("blocks"), list) else []
    full_text = str(period_reading_v1.get("full_text") or "").strip()
    block_issues: List[Dict[str, Any]] = []
    adjacent_issues: List[Dict[str, Any]] = []
    for idx, block in enumerate(blocks):
        if not isinstance(block, Mapping):
            continue
        text = str(block.get("text") or "").strip()
        issues = [
            *find_forbidden_public_copy_issues(text, check_directives=False),
            *find_technical_leakage(text, surface="body"),
            *find_organic_period_copy_issues(text),
        ]
        if issues:
            block_issues.append({"index": idx, "role": str(block.get("role") or ""), "issues": issues})
        if idx > 0 and isinstance(blocks[idx - 1], Mapping):
            previous_text = str(blocks[idx - 1].get("text") or "").strip()
            overlap = _adjacent_block_overlap_issues(previous_text, text)
            if overlap:
                adjacent_issues.append({"pair": [idx - 1, idx], "issues": overlap})
    full_text_issues = [
        *find_forbidden_public_copy_issues(full_text, check_directives=False),
        *find_technical_leakage(full_text, surface="body"),
        *find_organic_period_copy_issues(full_text),
    ]
    return {
        "blocks": block_issues,
        "adjacent_blocks": adjacent_issues,
        "full_text": full_text_issues,
    }


def _adjacent_block_overlap_issues(previous_text: str, current_text: str) -> List[Dict[str, Any]]:
    prev_tokens = _normalized_tokens(previous_text)
    curr_tokens = _normalized_tokens(current_text)
    if len(prev_tokens) < 4 or len(curr_tokens) < 4:
        return []
    prev_ngrams = {" ".join(prev_tokens[idx : idx + 4]) for idx in range(len(prev_tokens) - 3)}
    curr_ngrams = {" ".join(curr_tokens[idx : idx + 4]) for idx in range(len(curr_tokens) - 3)}
    overlap = sorted(prev_ngrams & curr_ngrams)
    if not overlap:
        return []
    return [{"code": "adjacent_block_ngram_overlap", "message": "Adjacent blocks repeat a 4-word phrase.", "match": overlap[0]}]


def _normalized_tokens(text: str) -> List[str]:
    normalized = phrase_lib_tr.strip_tech_tokens(str(text or "").lower())
    normalized = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in normalized)
    return [token for token in normalized.split() if token]


def _strip_prefix_if_present(text: str, prefix: str) -> str:
    token = str(text or "").strip()
    pref = str(prefix or "").strip()
    if pref and token.startswith(pref):
        return token[len(pref) :].strip()
    return token


def _soften_organic_fallback_text(text: str, *, role: str) -> str:
    token = str(text or "").strip()
    if not token:
        return ""
    replacements = (
        ("Asıl omurga burada yavaş ama kalıcı biçimde kuruluyor.", "Burada daha yavaş ama daha kalıcı bir çizgi oluşuyor."),
        ("Görünür olan eşik tam bu hatta toplanıyor.", "Burada görünür olan şey tek bir hatta toplanıyor."),
        ("Risk,", "Dikkat etmen gereken yer,"),
        ("ve senden daha bilinçli seçimler istiyor", "ve burada seçimini daha netleştirmen gerekiyor"),
        ("Bu dönem sende", "Bu sende"),
        ("Bu sende daha net seçim yapma biraz daha güçlendiriyor.", "Bu, daha net seçim yapabilmeni biraz daha güçlendiriyor."),
        ("kasını geliştiriyor", "biraz daha güçlendiriyor"),
        ("Bu tema daha çok ", ""),
        (" içinden görünür oluyor", " bu dönem daha görünür hale geliyor"),
        (" tarafında birkaç ayrı ihtiyaç aynı anda söz istiyor.", " tarafında birkaç ihtiyacı aynı anda dile getirmeye çalışıyorsun."),
        ("Aynı anda birkaç ayrı taraf söz istiyor.", "Aynı anda birkaç farklı ihtiyacı dile getirmeye çalışıyorsun."),
        ("Asıl ayrım burada:", "Bu yüzden mesele,"),
        ("Asıl ayrım, ", "Burada dikkat etmen gereken yer, "),
        ("Sende emeği daha rahat taşıyan bir görünürlük kuruyor.", "Emeğini daha rahat taşıyabildiğin bir görünürlük geliştiriyorsun."),
        ("Sende daha hafif ama daha seçilmiş bir taşıma biçimi kuruyor.", "Daha hafif ama daha seçilmiş bir taşıma biçimi geliştiriyorsun."),
        ("Sende sürtünmeyi taşıyabilen daha keskin bir iç koordinasyon kuruyor.", "Sürtünmeyi taşıdıkça içeride daha net bir koordinasyon kuruyorsun."),
        ("Sende sıkışmış kuvveti yöne çeviren daha net bir hareket alanı kuruyor.", "Sıkışan kuvveti daha net bir yöne çevirmeyi öğreniyorsun."),
        ("Sende daha sade ama daha sağlam taşınan bir duruş kuruyor.", "Daha sade ama daha sağlam taşınan bir duruş geliştiriyorsun."),
        ("Sende daha bütünlüklü bir yön kuruyor; içeride ayrı konuşan parçalar aynı cümlede toplanıyor.", "Daha bütünlüklü bir yön kuruyorsun; içeride ayrı konuşan parçaları aynı cümlede topluyorsun."),
        ("Sende büyüme zaten farklı parçaları aynı ritme alma ihtiyacıyla çalışıyor.", "Farklı parçalarını aynı ritme almayı öğreniyorsun."),
        ("sende büyüme zaten farklı parçaları aynı ritme alma ihtiyacıyla çalışıyor.", "Farklı parçalarını aynı ritme almayı öğreniyorsun."),
        ("Bu konu boşuna buradan açılmıyor; sende büyüme zaten farklı parçaları aynı ritme alma ihtiyacıyla çalışıyor.", "Farklı parçalarını aynı ritme almayı öğreniyorsun."),
    )
    for old, new in replacements:
        token = token.replace(old, new)
    if role == "hook" and token.startswith("Bu dönem hayatının bir alanı daha görünür hale geliyor"):
        token = token.replace(
            "Bu dönem hayatının bir alanı daha görünür hale geliyor",
            "Hayatının bir alanı daha görünür hale geliyor",
            1,
        )
    if token.startswith("Bu sende ") and token.endswith(" biraz daha güçlendiriyor."):
        token = token.replace("Bu sende ", "Bu, ", 1)
        token = token.replace(" biraz daha güçlendiriyor.", " çizgisini biraz daha güçlendiriyor.")
    token = re.sub(r"\b[Ss]ende ([^.]+?) kuruyor\.", lambda match: _second_person_build_clause(match.group(1)), token)
    token = re.sub(r"\s{2,}", " ", token).strip()
    return token


def _direct_scene_sentence(scene_seed: str, life_scene: str) -> str:
    seed = str(scene_seed or "").strip()
    scene = str(life_scene or "").strip()
    if scene:
        return f"{_capitalize_first(scene)} bu dönem daha görünür hale geliyor."
    if not seed:
        return ""
    direct = re.sub(r"^Bu tema daha çok\s+", "", seed, flags=re.IGNORECASE).strip()
    direct = re.sub(r"\s+içinden görünür oluyor\.?$", " bu dönem daha görünür hale geliyor", direct, flags=re.IGNORECASE).strip()
    return _capitalize_first(direct)


def _second_person_build_clause(clause: str) -> str:
    token = str(clause or "").strip()
    if not token:
        return ""
    if token.startswith("daha bütünlüklü bir yön"):
        return "Daha bütünlüklü bir yön kuruyorsun."
    if token.startswith("daha sade ama daha sağlam taşınan bir duruş"):
        return "Daha sade ama daha sağlam taşınan bir duruş geliştiriyorsun."
    if token.startswith("daha hafif ama daha seçilmiş bir taşıma biçimi"):
        return "Daha hafif ama daha seçilmiş bir taşıma biçimi geliştiriyorsun."
    return f"{_capitalize_first(token)} kuruyorsun."


def _polish_period_block_text(text: str, *, seen_sentences: set[str]) -> str:
    polished = _final_polish_tr(text)
    sentences = _split_sentences(polished)
    out: List[str] = []
    for sentence in sentences:
        cleaned = _capitalize_first(_final_polish_tr(sentence))
        if not cleaned:
            continue
        probe = " ".join(_normalized_tokens(cleaned))
        if probe and probe in seen_sentences:
            continue
        if probe:
            seen_sentences.add(probe)
        out.append(_ensure_sentence(cleaned))
    return " ".join(out).strip()


def _split_sentences(text: str) -> List[str]:
    token = str(text or "").strip()
    if not token:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", token) if part.strip()]


def _ensure_sentence(text: str) -> str:
    token = str(text or "").strip()
    if not token:
        return ""
    if token[-1] in ".!?":
        return token
    return f"{token}."


def _join_parts(*parts: str) -> str:
    out = " ".join(str(part or "").strip() for part in parts if str(part or "").strip()).strip()
    return out


def _dedupe_tokens(values: Sequence[str]) -> List[str]:
    out: List[str] = []
    seen: set[str] = set()
    for value in values:
        token = str(value or "").strip()
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


def _render_policy_process(policy: Mapping[str, Any], base: str) -> str:
    regime = _render_valence_intensity_process(policy)
    if regime:
        return regime
    text = _remove_period_opening_tic(base)
    context_sentence = _render_manifestation_context_sentence(policy)
    if context_sentence and context_sentence not in text:
        return f"{text} {context_sentence}".strip()
    return text


def _render_policy_higher_meaning(policy: Mapping[str, Any], base: str) -> str:
    specific = _render_framed_upper_meaning(policy)
    if specific:
        return specific

    regime = _render_valence_intensity_meaning(policy)
    if regime:
        return regime

    role = str(_policy_debug(policy).get("chapter_role") or "").strip()
    role_tail = _PERIOD_POLICY_ROLE_COPY.get(role, "")
    text = _remove_period_opening_tic(base)
    if text and role_tail and role_tail not in text:
        return f"{text} {role_tail}".strip()
    return text


def _render_policy_opening(policy: Mapping[str, Any]) -> str:
    valence = _policy_valence_mode(policy)
    intensity = _policy_intensity_mode(policy)
    life_scene = _policy_life_scene(policy)
    house = _safe_int(_policy_manifestation_context(policy).get("primary_house"))
    spine_line = _policy_spine_line(policy)

    if valence == "recognition" and intensity == "light":
        if house == 10 and life_scene:
            return f"{_capitalize_first(life_scene)} tarafında daha rahat görünüyorsun."
        return "Emeğin bu ara kendine daha doğal bir görünürlük buluyor."
    if valence == "release" and intensity == "light":
        if life_scene:
            return f"{_capitalize_first(life_scene)} tarafında her şeyi aynı anda içeri almak zorunda değilsin."
        return "Aynı şeyi aynı sıkılıkta taşımak zorunda değilsin."
    if valence == "integration" and intensity == "dense":
        if life_scene:
            return f"{_capitalize_first(life_scene)} tarafında birkaç ayrı ihtiyaç aynı anda söz istiyor."
        return "Aynı anda birkaç ayrı taraf söz istiyor."
    if valence == "maturation" and intensity == "medium":
        if spine_line == "primary_identity_line" and life_scene:
            return f"{_capitalize_first(life_scene)} içinde sözün daha seçilmiş bir ağırlık taşıyor."
        return "Üstlendiğin şey daha sakin ama daha kalıcı bir yere oturuyor."
    if valence == "momentum" and intensity == "dense":
        if spine_line == "primary_identity_line":
            return "İçinde yön almak isteyen hareket daha belirgin."
        return "İçeride duran kuvvet artık kendine daha net bir kanal arıyor."
    return ""


def _render_policy_growth_edge(policy: Mapping[str, Any], base: str) -> str:
    regime = _render_valence_intensity_growth_edge(policy)
    if regime:
        return regime
    frame = _policy_rhetorical_frame(policy)
    intent = _policy_meaning_intent(policy)
    release_variant = _release_variant(policy)
    life_scene = _policy_life_scene(policy)
    house = _safe_int(_policy_manifestation_context(policy).get("primary_house"))
    if frame == "threshold":
        if life_scene:
            return f"Asıl ayrım, {life_scene} tarafında görünür olan şeyi hemen son kararın gibi taşımamak."
        if intent == "responsibility_selection":
            return "Karar şurada: yükü taşımakla onun arkasında durmak aynı şey değil."
        if intent in {"activation", "visibility_alignment", "self_naming"}:
            return "Karar şurada: hazır hissetmekle kendini ortaya koymak aynı şey değil."
        return "Karar şurada: eski refleksi sürdürmekle yeni yönünü sahiplenmek aynı şey değil."
    if frame == "sorting":
        if intent == "responsibility_selection":
            return "Önce yükü çoğaltmak değil, hangisini gerçekten seçtiğini netleştirmek gerekiyor."
        return "Burada aynı görünen iki yön var; hangisinin gerçekten sana ait olduğunu seçmen gerekiyor."
    if frame == "calibration":
        if life_scene:
            return f"Asıl ayar, {life_scene} tarafında neyi açıp neyi biraz geride tuttuğunu daha bilinçli seçmek."
        return "İki uçtan birine gitmek gerekmiyor; küçük ayar bu temayı daha doğru taşır."
    if frame == "mirror":
        return "Karşı tarafta büyüyen tepki, sende sessizce çalışan beklentiyi de ortaya çıkarır."
    if frame == "reframe" and life_scene:
        return f"Asıl ayrım, {life_scene} tarafında büyüyen tepkiyi bütün hikayenin yerine koymamak."
    if frame == "release":
        return f"Burada asıl hareket, her şeyi aynı sıkılıkta tutmak yerine biraz {release_variant}."
    if frame == "embodiment":
        return "Bunu sadece düşüncede değil, omuzlarında, hızında ve bedeninin verdiği cevapta da okuyabilirsin."
    if frame == "naked":
        if life_scene and house == 3:
            return f"Asıl ayrım, {life_scene} içinden yükselen şeyi hemen sonuca çevirmemek."
        if life_scene and house == 10:
            return f"Asıl ayrım, {life_scene} tarafında görünür olan yükü hemen kimliğinin tamamı sanmamak."
        return "Bu, savunmayı çözmek değil." if _policy_event_nature(policy) == "dissolution" else "Bu, her şeyi aynı anda netleştirmek zorunda kalmak değil."

    text = _remove_period_opening_tic(base)
    prefix = "Buradaki eşik, "
    if text.startswith(prefix):
        edge = text[len(prefix) :].strip()
        if edge:
            return f"Asıl ayrım burada: {edge}"
    return text


def _render_policy_build(policy: Mapping[str, Any], base: str) -> str:
    valence = _policy_valence_mode(policy)
    intensity = _policy_intensity_mode(policy)
    if valence == "recognition" and intensity == "light":
        return "Sende emeği daha rahat taşıyan bir görünürlük kuruyor."
    if valence == "release" and intensity == "light":
        return "Sende daha hafif ama daha seçilmiş bir taşıma biçimi kuruyor."
    if valence == "integration" and intensity == "dense":
        return "Sende sürtünmeyi taşıyabilen daha keskin bir iç koordinasyon kuruyor."
    if valence == "momentum" and intensity == "dense":
        return "Sende sıkışmış kuvveti yöne çeviren daha net bir hareket alanı kuruyor."
    if valence == "maturation" and intensity == "medium":
        return "Sende daha sade ama daha sağlam taşınan bir duruş kuruyor."
    return base


def _render_policy_reason_line(policy: Mapping[str, Any], base: str) -> str:
    spine_line = _policy_spine_line(policy)
    event_nature = _policy_event_nature(policy)
    if spine_line == "work_visibility_line" and event_nature == "responsibility":
        return "Görünürlükle sorumluluk aynı yerde konuştuğunda, doğru yükü seçmek uzun vadeli yönünü de netleştirir."
    if spine_line == "work_visibility_line" and event_nature == "control":
        return "Görünürlük ve güç aynı yerde toplandığında, kontrol etmek istediğin şeyin altında hangi emeği koruduğun daha belirginleşir."
    if spine_line == "work_visibility_line" and event_nature == "courage":
        return "Görünürlük burada sadece öne çıkmak değil; yaptığın işe biraz daha rahat yer açabilmek."
    if spine_line == "relational_line" and event_nature in {"boundary", "responsibility"}:
        return "Yakınlık ve güven aynı yerde çalıştığında, mesafe ceza değil daha dürüst bir düzen kurma biçimi olabilir."
    if spine_line == "relational_line":
        return "Yakınlık burada sadece bağ kurmak değil; bağın içinde kendini ne kadar geride bırakmadığını görmek."
    if spine_line == "shadow_protection_line":
        return "Korunma refleksi bu temayla temas ettiğinde, neyin seni tuttuğu ve neyin yavaşlattığı daha net ayrılır."
    if spine_line == "emotional_regulation_line":
        return "Duygu ve güven aynı hatta çalıştığında, küçük tepkiler bile daha eski bir ihtiyacın yerini gösterebilir."
    if spine_line == "primary_identity_line":
        return "Kimlik ve yön aynı hatta çalıştığında, küçük bir cümle bile nerede durduğunu daha net gösterebilir."
    return _remove_reason_cliche(base)


def _render_framed_upper_meaning(policy: Mapping[str, Any]) -> str:
    frame = _policy_rhetorical_frame(policy)
    intent = _policy_meaning_intent(policy)
    spine_line = _policy_spine_line(policy)
    event_nature = _policy_event_nature(policy)
    release_variant = _release_variant(policy)
    life_scene = _policy_life_scene(policy)

    if frame == "mirror":
        if intent in {"trust_calibration", "boundary_repair"}:
            return "Karşındaki tarafta belirginleşen şey, sende güveni nasıl kurduğunu da görünür yapıyor."
        return "Dışarıda gördüğün tepki, içeride hangi beklentinin sessizce çalıştığını da gösteriyor."
    if frame == "calibration":
        if intent == "trust_calibration":
            if life_scene:
                return f"Konu daha sert olmak değil; özellikle {life_scene} tarafında yakınlıkla mesafeyi aynı cümlede tutacak ayarı bulmak."
            return "Konu daha sert olmak değil; yakınlıkla mesafeyi aynı cümlede tutacak ayarı bulmak."
        return "Burada her şeyi büyütmek gerekmiyor; daha doğru ayar çoğu şeyi değiştirir."
    if frame == "sorting":
        if intent == "responsibility_selection":
            return "Şimdi ayırman gereken şey, gerçekten sana ait olan yükle sırf alışkanlıktan taşıdığın yük."
        return "Burada aynı görünen iki yön var; hangisinin gerçekten sana ait olduğunu seçmen gerekiyor."
    if frame == "threshold":
        if life_scene:
            return f"Karar şurada: {life_scene} tarafında hazır hissetmekle harekete geçmek aynı şey değil."
        if intent == "responsibility_selection":
            return "Karar şurada: yükü taşımakla onun arkasında durmak aynı şey değil."
        if intent in {"activation", "visibility_alignment", "self_naming"}:
            return "Karar şurada: hazır hissetmekle harekete geçmek aynı şey değil."
        return "Karar şurada: eski refleksi sürdürmekle yeni yönünü sahiplenmek aynı şey değil."
    if frame == "reframe":
        if spine_line == "shadow_protection_line" and event_nature == "dissolution":
            return "İlk bakışta bu dağılma gibi durabilir; ama altında her şeyi aynı sıkılıkta tutmama ihtiyacı var."
        if spine_line == "relational_line":
            if life_scene:
                return f'İlk bakışta bu bir "kim haklı" meselesi gibi görünebilir; ama özellikle {life_scene} tarafında, altında kendini ifade ederken nasıl korunduğun var.'
            return 'İlk bakışta bu bir "kim haklı" meselesi gibi görünebilir; ama altında, kendini ifade ederken nasıl korunduğun var.'
        return "İlk bakışta görünen şey tek mesele değil; altında daha kişisel bir yön ayarı var."
    if frame == "release":
        return f"Burada asıl hareket, her şeyi aynı yerde tutmak değil; biraz {release_variant}."
    if frame == "embodiment":
        if spine_line == "primary_identity_line":
            return "Bunu sadece zihninde değil, omuzlarında, hızında ve attığın ilk adımda da hissedebilirsin."
        return "Bu tema düşüncede kalmıyor; nefesinde, bedenindeki ağırlıkta ve ritminde de yer tutuyor."
    if frame == "naked":
        if spine_line == "shadow_protection_line" and event_nature == "dissolution":
            if life_scene:
                return f"Bu, savunmayı bırakmak değil. Özellikle {life_scene} tarafında beliren şeyi aceleyle çözmek de değil."
            return "Bu, savunmayı bırakmak değil."
        if life_scene:
            return f"Bu, kendini zorlamak değil. Özellikle {life_scene} tarafında büyüyen şeyi hemen sonuca çevirmek de değil."
        return "Bu, kendini zorlamak değil."
    return ""


def _render_valence_intensity_process(policy: Mapping[str, Any]) -> str:
    valence = _policy_valence_mode(policy)
    intensity = _policy_intensity_mode(policy)
    life_scene = _policy_life_scene(policy)
    spine_line = _policy_spine_line(policy)

    if valence == "integration" and intensity == "dense":
        scene = (
            f"{_capitalize_first(life_scene)} tarafında bu çizgi pürüzsüz bir akış kadar rahat akmıyor; "
            if life_scene
            else "Bu çizgi pürüzsüz bir akış kadar rahat akmıyor; "
        )
        if spine_line == "relational_line":
            return (
                f"{scene}yakınlıkla kendi alanın aynı anda söz istiyor. "
                "Sürtünmenin kendisi uyumsuzluk değil; ayrı duran ihtiyaçların birbirini öğrenmesi."
            )
        return (
            f"{scene}ayrı duran iki taraf aynı anda yer arıyor. "
            "Sürtünmenin kendisi çelişki değil; iki alan birbirini öğreniyor."
        )
    if valence == "recognition" and intensity == "light":
        if life_scene:
            return (
                f"{_capitalize_first(life_scene)} tarafında daha rahat görünüyorsun. "
                "Bir süredir içeride tuttuğun emek artık sadece hazırlıkta kalmak istemiyor."
            )
        return "Yaptığın şey artık sessiz çalışmıyor; emeğin daha doğal bir görünürlük kazanıyor."
    if valence == "opening" and intensity == "light":
        if life_scene:
            return f"{_capitalize_first(life_scene)} tarafında bir kapı zorlamadan aralanıyor; akış biraz daha doğal geliyor."
        return "Burada bir kapı zorlamadan aralanıyor; destek bu kez daha doğal akıyor."
    if valence == "maturation" and intensity == "medium":
        if spine_line == "primary_identity_line" and life_scene:
            return f"{_capitalize_first(life_scene)} içinde kullandığın ses daha az acele, daha çok duruş taşıyor."
        return "Ağırlık bu kez sadece yük gibi değil; yavaş yavaş yerine oturan bir düzen gibi hissediliyor."
    if valence == "release" and intensity == "light":
        return "Bir süredir aynı sıkılıkta tuttuğun şey hafifliyor; burada çözülme uzaklaşmak değil, biraz yer açmak."
    if valence == "momentum" and intensity == "dense":
        if spine_line == "primary_identity_line":
            return "İçeride bir hareket var; pürüzsüz değil ama yönünü daha açık alma isteği artık geri çekilmiyor."
        return "İçeride bir hareket var; pürüzsüz değil ama sıkışmış kuvvetin yön bulduğu yer tam da burası."
    return ""


def _render_valence_intensity_meaning(policy: Mapping[str, Any]) -> str:
    valence = _policy_valence_mode(policy)
    intensity = _policy_intensity_mode(policy)
    spine_line = _policy_spine_line(policy)
    if valence == "integration" and intensity == "dense":
        return (
            "Bu yoğunluk sadece sürtünme değil; ayrı duran parçaların aynı düzen içinde yer araması. "
            "Pürüzsüz bir akış bu kası kuramazdı."
        )
    if valence == "recognition" and intensity == "light":
        return "Konu kendini kanıtlamak değil; sende biriken emeğin daha doğal bir görünürlük bulması."
    if valence == "opening" and intensity == "light":
        return "Burada zorlama gerektirmeyen bir açılma var; akış kapıyı kendi hızında aralıyor."
    if valence == "maturation" and intensity == "medium":
        if spine_line == "primary_identity_line":
            return "Mesele daha çok yük almak değil; nerede durduğunu daha sade ama daha sağlam taşımak."
        return "Mesele daha çok yük almak değil; zaten taşıdığın şeyi daha seçilmiş ve daha sağlam bir düzene yerleştirmek."
    if valence == "release" and intensity == "light":
        return "Bu uzaklaşmak değil; seni gereksiz yere yoran şeyi aynı yoğunlukta içeri almamak."
    if valence == "momentum" and intensity == "dense":
        return "Baskı burada sadece fren değil; sıkışmış kuvvetin kendine daha net bir yön açması."
    return ""


def _render_valence_intensity_growth_edge(policy: Mapping[str, Any]) -> str:
    valence = _policy_valence_mode(policy)
    intensity = _policy_intensity_mode(policy)
    life_scene = _policy_life_scene(policy)
    spine_line = _policy_spine_line(policy)
    if valence == "integration" and intensity == "dense":
        if life_scene:
            return (
                f"Asıl ayrım, {life_scene} tarafındaki sürtünmeyi uyumsuzluk sanmamak. "
                "Ayrı duran ihtiyaçlar burada birbirini öğreniyor."
            )
        return "Asıl ayrım, sürtünmeyi uyumsuzluk sanmamak; iki ayrı kuvvet burada aynı anda çalışmayı öğreniyor."
    if valence == "recognition" and intensity == "light":
        return "Asıl ayrım, görünür olmayı kendini kanıtlama baskısıyla karıştırmamak."
    if valence == "opening" and intensity == "light":
        return "Asıl ayrım, açılan kapıyı aceleyle zorlamak yerine doğal desteğin ritmini fark etmek."
    if valence == "maturation" and intensity == "medium":
        if spine_line == "primary_identity_line" and life_scene:
            return f"Asıl ayrım, {life_scene} içinden hızlı cevap vermekle nerede durduğunu söylemek arasındaki farkı kaçırmamak."
        return "Asıl ayrım, ağırlığı hemen engel sanmamak; burada yerine oturan şeyin de bir işlevi var."
    if valence == "release" and intensity == "light":
        return "Asıl ayrım, hafiflemenin gevşemek değil, biraz daha seçerek taşımak olduğunu görmek."
    if valence == "momentum" and intensity == "dense":
        return "Asıl ayrım, baskıyı fren gibi okumamak; burada hareketi keskinleştiren de aynı yoğunluk."
    return ""


def _policy_debug(policy: Mapping[str, Any]) -> Dict[str, Any]:
    debug = policy.get("debug")
    return dict(debug) if isinstance(debug, Mapping) else {}


def _policy_spine_line(policy: Mapping[str, Any]) -> str:
    return str(_policy_debug(policy).get("spine_line") or "").strip()


def _policy_event_nature(policy: Mapping[str, Any]) -> str:
    return str(_policy_debug(policy).get("event_nature") or "").strip()


def _policy_meaning_intent(policy: Mapping[str, Any]) -> str:
    return str(policy.get("meaning_intent") or _policy_debug(policy).get("meaning_intent") or "").strip()


def _policy_rhetorical_frame(policy: Mapping[str, Any]) -> str:
    return str(policy.get("rhetorical_frame") or _policy_debug(policy).get("rhetorical_frame") or "").strip()


def _policy_valence_mode(policy: Mapping[str, Any]) -> str:
    return str(policy.get("valence_mode") or _policy_debug(policy).get("valence_mode") or "").strip()


def _policy_intensity_mode(policy: Mapping[str, Any]) -> str:
    return str(policy.get("intensity_mode") or _policy_debug(policy).get("intensity_mode") or "").strip()


def _policy_event_bodies(policy: Mapping[str, Any]) -> List[str]:
    raw = _policy_debug(policy).get("event_bodies")
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return []
    return [str(item).strip().lower() for item in raw if str(item).strip()]


def _policy_manifestation_context(policy: Mapping[str, Any]) -> Dict[str, Any]:
    context = policy.get("manifestation_context")
    if isinstance(context, Mapping):
        return dict(context)
    debug_context = _policy_debug(policy).get("manifestation_context")
    if isinstance(debug_context, Mapping):
        return dict(debug_context)
    return {}


def _policy_life_scene(policy: Mapping[str, Any]) -> str:
    return str(_policy_manifestation_context(policy).get("life_scene") or "").strip()


def _render_manifestation_context_sentence(policy: Mapping[str, Any]) -> str:
    context = _policy_manifestation_context(policy)
    life_scene = str(context.get("life_scene") or "").strip()
    if not life_scene:
        return ""

    house = _safe_int(context.get("primary_house"))
    spine_line = _policy_spine_line(policy)
    event_nature = _policy_event_nature(policy)
    release_strengthened = bool(context.get("release_strengthened"))

    if spine_line == "work_visibility_line" and event_nature == "responsibility" and house == 6:
        return (
            f"Bu tema {life_scene} içinden çalıştığı için, küçük aksaklıklar bile "
            '"ben bunu böyle taşımaya devam edebilir miyim?" sorusunu büyütebilir.'
        )
    if spine_line == "work_visibility_line" and event_nature == "responsibility" and house == 10:
        return f"Burada sahne daha çok {life_scene}; senden beklenen duruşla taşıdığın yük aynı anda görünür oluyor."
    if spine_line == "work_visibility_line" and event_nature == "courage" and house == 10:
        return f"Burada sahne {life_scene}; yaptığın şey öne çıkarken ekstra kanıt araman gerekmiyor."
    if spine_line == "relational_line" and event_nature in {"boundary", "responsibility"} and house == 3:
        return (
            f"Bu kez mesele büyük açıklamalardan çok {life_scene} içinden çalışıyor; geciken bir cevap ya da "
            "söylenmeyen bir cümle daha büyük bir beklentiyi gösterebilir."
        )
    if spine_line == "relational_line" and event_nature in {"boundary", "responsibility"} and house == 7:
        return f"Burada sahne {life_scene}; sınır uzaklaşmak değil, karşılıklı zemini daha dürüst kurmak."
    if spine_line == "shadow_protection_line" and event_nature == "dissolution" and house == 12:
        return (
            f"{_capitalize_first(life_scene)} içinde belirsizliği hemen anlamla doldurmak yerine, neyin sezgi neyin "
            "bulanıklık olduğunu ayırmak daha iyi çalışır."
        )
    if house == 6:
        return f"Bu tema {life_scene} içinde daha belirgin çalışıyor; neyin sürdürülebildiği burada daha hızlı anlaşılıyor."
    if house == 10:
        return f"Bu tema {life_scene} tarafında görünür oluyor; mesele sadece sonuç değil, nasıl bir duruş taşıdığın."
    if house == 3:
        return f"Bu tema {life_scene} içinden büyüyor; küçük cümleler bile alttaki daha büyük meseleyi görünür kılabilir."
    if house == 12:
        if release_strengthened:
            return f"Bu tema {life_scene} tarafında çözülüyor; bazı şeyleri aynı sıkılıkta tutmamak burada daha iyi çalışır."
        return f"Bu tema {life_scene} tarafında sessiz ama belirgin; hızlı anlamlandırmak yerine biraz yavaşlamak iyi gelir."
    return str(context.get("context_seed") or "").strip()


def _release_variant(policy: Mapping[str, Any]) -> str:
    bodies = set(_policy_event_bodies(policy))
    if "neptune" in bodies:
        return "yer açmak"
    if "pluto" in bodies:
        return "bir yükü indirmek"
    if "south node" in bodies or "south_node" in bodies or "southnode" in bodies:
        return "uğurlamak"
    if _policy_event_nature(policy) == "dissolution":
        return "yer açmak"
    return "artık taşımamayı seçmek"


def _remove_period_opening_tic(text: str) -> str:
    value = str(text or "").strip()
    if value.startswith("Bu dönem "):
        return _capitalize_first(value[len("Bu dönem ") :].strip())
    return value


def _remove_reason_cliche(text: str) -> str:
    value = _remove_period_opening_tic(text)
    for prefix in (
        "Bu konu boşuna buradan açılmıyor; ",
        "Bu konu boşuna buradan açılmıyor; sende ",
        "Haritanda ",
    ):
        if value.startswith(prefix):
            value = value[len(prefix) :].strip()
    return value


def _capitalize_first(text: str) -> str:
    value = str(text or "").strip()
    if not value:
        return ""
    return f"{value[:1].upper()}{value[1:]}"


def _period_voice_policy_events(
    canonical_period_spine: Mapping[str, Any] | None,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> List[Dict[str, Any]]:
    events = [dict(item) for item in (spine, *supports) if isinstance(item, Mapping)]
    period_spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    matched_ids = {
        str(item).strip()
        for item in (period_spine.get("matched_event_ids") or [])
        if str(item).strip()
    }
    if not matched_ids:
        return events
    matched = [
        event
        for event in events
        if str(event.get("event_id") or "").strip() in matched_ids
    ]
    return matched or events


def _canonical_backing_node_ids(canonical_period_spine: Mapping[str, Any] | None) -> List[str]:
    period_spine = canonical_period_spine if isinstance(canonical_period_spine, Mapping) else {}
    values: List[str] = []
    for key in ("target_node_id", "target_node_ids", "backing_node_ids"):
        raw = period_spine.get(key)
        if isinstance(raw, Sequence) and not isinstance(raw, (str, bytes)):
            candidates = raw
        else:
            candidates = [raw]
        for candidate in candidates:
            token = str(candidate or "").strip()
            if token and token not in values:
                values.append(token)
    return values


def _select_spine_and_supports(period_core: Mapping[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    events_raw = (
        period_core.get("featured_events")
        or period_core.get("events")
        or period_core.get("items")
        or []
    )
    events = [dict(e) for e in events_raw if isinstance(e, Mapping)]
    if not events:
        return ({}, [])

    def story_score(e: Mapping[str, Any]) -> float:
        return _safe_float(e.get("story_score"), 0.0)

    def selection_index(e: Mapping[str, Any]) -> int:
        try:
            return int(e.get("selection_index"))
        except (TypeError, ValueError):
            return 999

    def rank_key(e: Mapping[str, Any]) -> Tuple[float, float, int, int]:
        strength = _safe_float(e.get("strength"), 0.0)
        orb = _safe_float(e.get("orb_deg"), 999.0)
        bucket = str(e.get("bucket") or "").lower()
        phase = str(e.get("phase") or "").lower()
        bucket_score = 2 if bucket == "long" else (1 if bucket == "medium" else 0)
        phase_score = 2 if phase in {"exact", "exactish"} else (1 if phase == "applying" else 0)
        return (story_score(e), strength, -orb, bucket_score, phase_score, -selection_index(e))

    sorted_events = sorted(events, key=rank_key, reverse=True)
    spine = sorted_events[0]
    used_ids = {str(spine.get("event_id") or "")}
    supports: List[Dict[str, Any]] = []

    for role in _support_role_order(_chapter_role_name(spine)):
        candidate = next(
            (
                event
                for event in sorted_events[1:]
                if str(event.get("event_id") or "") not in used_ids and _chapter_role_name(event) == role
            ),
            None,
        )
        if candidate is not None:
            supports.append(candidate)
            used_ids.add(str(candidate.get("event_id") or ""))
        if len(supports) >= 2:
            break

    if len(supports) < 2:
        for event in sorted_events[1:]:
            event_id = str(event.get("event_id") or "")
            if event_id in used_ids:
                continue
            supports.append(event)
            used_ids.add(event_id)
            if len(supports) >= 2:
                break
    return (spine, supports)


def _build_big_picture(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    domain = _infer_domain_tr(spine)
    seed = _seed_for(str(spine.get("event_id") or "spine"))
    return phrase_lib_tr.period_big_picture(
        domain=domain,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _period_life_scene(house: int | None, detail: str = "short") -> str:
    if not house:
        return "hayatının bu alanı"
    pack = getattr(text_quality_tr, "HOUSE_LIFE_TRANSLATIONS_TR", {})
    return str(pack.get(int(house), {}).get(detail) or "hayatının bu alanı")


def _build_period_opening(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    start_house, end_house = _infer_start_end_houses(spine)
    start_scene = _period_life_scene(start_house, "full")
    end_scene = _period_life_scene(end_house, "short")
    spine_role = _chapter_role_name(spine)
    support_line = ""
    if supports:
        support_house, support_target = _infer_start_end_houses(supports[0])
        support_line = (
            f" Arkadaki destek hattı {_period_life_scene(support_house, 'short')} tarafından açılıp "
            f"{_period_life_scene(support_target, 'short')} alanına güç taşıyor."
        )
    return (
        f"{CHAPTER_ROLE_OPENING_TR.get(spine_role, 'Bu dönem ana tema burada toplanıyor.')} "
        f"Önce {start_scene} tarafını hassaslaştırıyor, sonra bunun etkisi {end_scene} alanında belirginleşiyor."
        f"{support_line}"
    ).strip()


def _with_chapter_role_opening(opening: str, spine: Mapping[str, Any]) -> str:
    role = _chapter_role_name(spine)
    prefix = CHAPTER_ROLE_OPENING_TR.get(role, "").strip()
    text = str(opening or "").strip()
    if not prefix or not text:
        return text or prefix
    lowered = text.lower()
    prefix_probe = prefix.split(".")[0].strip().lower()
    if prefix_probe and prefix_probe in lowered:
        return text
    return f"{prefix} {text}".strip()


# S0-4: Natal promise → period_opening bağlam cümlesi.
# Sadece verdict in {strong, exact} + bilinen domain (HOUSE_DOMAIN_HINTS)
# + "general" değil → bir cümle döner. Aksi halde None → mevcut davranış.
_PROMISE_STRONG_VERDICTS = frozenset({"strong", "exact"})


def _build_canonical_promise_prefix(
    canonical_period_spine: Mapping[str, Any] | None,
) -> Optional[str]:
    return build_period_prefix_from_period_spine(canonical_period_spine)


def _build_promise_prefix(
    natal_promise: Mapping[str, Any] | None,
    spine: Mapping[str, Any],
) -> Optional[str]:
    if not isinstance(natal_promise, Mapping):
        return None
    verdict = str(natal_promise.get("verdict") or "").strip().lower()
    if verdict not in _PROMISE_STRONG_VERDICTS:
        return None
    connected = natal_promise.get("connected_points")
    if not isinstance(connected, Sequence) or not connected:
        return None
    first = connected[0] if isinstance(connected[0], Mapping) else {}
    house = _safe_int(first.get("house"))
    if house is None:
        return None
    domain = HOUSE_DOMAIN_HINTS.get(house, "general")
    if domain == "general":
        return None
    variants = getattr(phrase_lib_tr, "PROMISE_DOMAIN_CONTEXT_TR", {}).get(domain)
    if not variants:
        return None
    seed = str(spine.get("event_id") or "") + "|promise"
    idx = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16) % len(variants)
    return str(variants[idx]).strip() or None


def _build_growth_edge(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    _ = ctx
    aspect = str(spine.get("aspect") or "").strip().lower()
    transit_body = str(spine.get("transit_body") or "").strip().lower()
    start_house, _ = _infer_start_end_houses(spine)
    start_scene = _period_life_scene(start_house, "short")
    if transit_body == "neptune" and aspect in {"square", "opposition", "conjunction"}:
        return f"En kritik eşik, {start_scene} tarafındaki muğlaklığı yalnızca hisle yönetmeye çalışmak. Netleşmeyen kısım bir süre sonra seni gereksiz açıklama ve yorgunluğa itebilir."
    if transit_body == "uranus" and aspect in {"trine", "sextile"}:
        return f"En büyük risk, {start_scene} tarafında açılan hevesi aynı anda çok yere dağıtmak. Hız arttıkça ölçü kayarsa kazanç derinleşmeden sönebilir."
    if transit_body == "pluto":
        return "Buradaki eşik, seçiciliği kontrol etme ihtiyacına çevirmemek. Gücü toplamak isterken yakınlığı ve işbirliğini kurutma riski var."
    return f"Bu dönemde asıl dikkat edilmesi gereken şey, {start_scene} tarafındaki ilk tepkiyi sonuç sanmak. Süreç senden biraz daha sabır ve netlik istiyor."


def _build_life_expression(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    _ = ctx
    start_house, end_house = _infer_start_end_houses(spine)
    start_scene = _period_life_scene(start_house, "short")
    end_scene = _period_life_scene(end_house, "short")
    if end_house == 7:
        return f"Günlük hayatta bu etki en çok {start_scene} tarafındaki açıklık ihtiyacı üzerinden çalışır; karşılığını ise ilişkilerde daha net beklenti ve daha temiz sınır olarak görürsün."
    if end_house == 11:
        return f"Günlük hayatta önce {start_scene} alanında seçicilik artar; sonra bu durum arkadaş çevresi, ekipler ve gelecek planları içinde yeni bir eleme yaratır."
    return f"Günlük hayatta bu süreci en çok {start_scene} ile {end_scene} arasındaki bağlantıda hissedersin. Biri kıpırdar, diğeri yön değiştirir."


def _build_what_it_builds(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    promise_theme = _select_promise_theme(ctx.natal_promise, spine, ctx.canonical_period_spine)
    skill_gain = _infer_skill_gain_tr(spine, promise_theme)
    role_line = CHAPTER_ROLE_BUILD_TR.get(_chapter_role_name(spine), "")
    return f"Bu dönem sende {skill_gain} kasını geliştiriyor. {role_line}".strip()


def _chapter_role_name(event: Mapping[str, Any]) -> str:
    chapter_role = event.get("chapter_role") if isinstance(event.get("chapter_role"), Mapping) else {}
    role = str(chapter_role.get("role") or "").strip().lower()
    return role or "builder"


def _support_role_order(spine_role: str) -> List[str]:
    mapping = {
        "builder": ["opener", "peak", "integrator", "release"],
        "opener": ["builder", "peak", "integrator", "release"],
        "peak": ["builder", "release", "integrator", "opener"],
        "release": ["builder", "integrator", "peak", "opener"],
        "integrator": ["builder", "opener", "peak", "release"],
    }
    return mapping.get(spine_role, ["builder", "opener", "peak", "integrator"])


def _build_chain_paragraph(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    transit_body = str(spine.get("transit_body") or "")
    aspect = str(spine.get("aspect") or "")
    natal_point = str(spine.get("natal_point") or "")

    start_house, end_house = _infer_start_end_houses(spine)
    start_theme = HOUSE_THEME_TR.get(start_house, "günlük hayat")
    end_theme = HOUSE_THEME_TR.get(end_house, "hayat yönü")

    angle_chain = _angle_chain_from_event(spine)
    target_chain = _target_chain_from_event(spine)
    if natal_point in ANGLE_TO_CUSP_HOUSE:
        angle_chain = angle_chain or _angle_ruler_chain(ctx.chart_snapshot, natal_point)
    elif natal_point:
        target_chain = target_chain or _planet_target_chain(ctx.chart_snapshot, natal_point)

    seed = _seed_for(str(spine.get("event_id") or "chain"))

    return phrase_lib_tr.period_mechanism_chain(
        transit_body=transit_body,
        aspect=aspect,
        natal_point=natal_point,
        angle_chain=angle_chain,
        target_chain=target_chain,
        start_theme=start_theme,
        end_theme=end_theme,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _build_upper_meaning(
    ctx: PeriodStoryContext,
    spine: Mapping[str, Any],
    supports: Sequence[Mapping[str, Any]],
) -> str:
    promise_theme = _select_promise_theme(ctx.natal_promise, spine, ctx.canonical_period_spine)
    skill_gain = _infer_skill_gain_tr(spine, promise_theme)
    seed = _seed_for(str(spine.get("event_id") or "upper"))
    return phrase_lib_tr.period_upper_meaning(
        promise_theme=promise_theme,
        skill_gain=skill_gain,
        seed=seed,
        enable_fun=ctx.enable_fun,
    )


def _angle_ruler_chain(snapshot: Mapping[str, Any], angle: str) -> Optional[Dict[str, Any]]:
    house_cusps = snapshot.get("house_cusps") or snapshot.get("houseCusps")
    bodies_map = _snapshot_bodies_map(snapshot)
    if angle not in ANGLE_TO_CUSP_HOUSE:
        return None

    cusp_house = ANGLE_TO_CUSP_HOUSE[angle]
    cusp = _cusp_for_house(house_cusps, cusp_house)
    sign = str((cusp or {}).get("sign") or "").strip()
    if not sign:
        return None

    ruler = RULERS.get(sign)
    ruler_body = bodies_map.get(str(ruler or "").lower()) or {}

    return {
        "angle": angle,
        "sign": sign,
        "ruler": ruler,
        "ruler_house": _safe_int(ruler_body.get("house")),
        "ruler_sign": str(ruler_body.get("sign") or "").strip(),
    }


def _angle_chain_from_event(event: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    angle = derived.get("angle") if isinstance(derived.get("angle"), Mapping) else {}
    angle_name = str(angle.get("name") or event.get("natal_point") or "").strip().upper()
    if angle_name not in ANGLE_TO_CUSP_HOUSE:
        return None
    sign = str(angle.get("sign") or "").strip()
    ruler = str(angle.get("ruler") or "").strip()
    if not (sign and ruler):
        return None
    return {
        "angle": angle_name,
        "sign": sign,
        "ruler": ruler,
        "ruler_house": _safe_int(angle.get("ruler_house")),
        "ruler_sign": str(angle.get("ruler_sign") or "").strip(),
    }


def _planet_target_chain(snapshot: Mapping[str, Any], planet: str) -> Optional[Dict[str, Any]]:
    bodies_map = _snapshot_bodies_map(snapshot)
    pb = bodies_map.get(planet.lower())
    if not isinstance(pb, Mapping):
        return None

    sign = str(pb.get("sign") or "").strip()
    return {
        "planet": planet,
        "sign": sign,
        "house": _safe_int(pb.get("house")),
        "dispositor": RULERS.get(sign),
    }


def _target_chain_from_event(event: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    derived = event.get("derived_context") if isinstance(event.get("derived_context"), Mapping) else {}
    target = derived.get("natal_target") if isinstance(derived.get("natal_target"), Mapping) else {}
    planet = str(target.get("name") or event.get("natal_point") or "").strip()
    if not planet or planet.upper() in ANGLE_TO_CUSP_HOUSE:
        return None
    sign = str(target.get("sign") or "").strip()
    if not sign:
        return None
    return {
        "planet": planet,
        "sign": sign,
        "house": _safe_int(target.get("house")),
        "dispositor": str(target.get("dispositor") or RULERS.get(sign) or "").strip() or None,
    }


def _infer_start_end_houses(event: Mapping[str, Any]) -> Tuple[int, int]:
    houses = event.get("houses") if isinstance(event.get("houses"), Mapping) else {}
    start_house = _safe_int(houses.get("transit_in_natal_house")) or 3
    end_house = _safe_int(houses.get("natal_point_house")) or 1
    return (start_house, end_house)


def _infer_domain_tr(event: Mapping[str, Any]) -> str:
    tags = event.get("tags") if isinstance(event.get("tags"), list) else []
    tag_set = {str(tag).lower() for tag in tags}
    if "relationships" in tag_set:
        return "ilişki dili"
    if "mind" in tag_set or "communication" in tag_set:
        return "zihin ve iletişim"
    if "career" in tag_set:
        return "yön ve görünürlük"
    if "home" in tag_set:
        return "temel düzen"
    if "self" in tag_set:
        return "kimlik ve duruş"
    _, end_house = _infer_start_end_houses(event)
    return HOUSE_THEME_TR.get(end_house, "hayat yönü")


def _select_promise_theme(
    natal_promise: Mapping[str, Any],
    spine: Mapping[str, Any],
    canonical_period_spine: Mapping[str, Any] | None = None,
) -> str:
    canonical_theme = select_period_theme_from_spine(canonical_period_spine)
    if canonical_theme:
        return canonical_theme
    themes = natal_promise.get("themes") or natal_promise.get("promiseThemes") or []
    if isinstance(themes, list) and themes:
        return str(themes[0])
    drivers = natal_promise.get("drivers")
    if isinstance(drivers, list) and drivers:
        first = drivers[0]
        if isinstance(first, Mapping):
            label = str(first.get("label") or first.get("theme") or "").strip()
            if label:
                return label
        label = str(first).strip()
        if label:
            return label
    return _infer_domain_tr(spine)


def _infer_skill_gain_tr(spine: Mapping[str, Any], promise_theme: str) -> str:
    transit_body = str(spine.get("transit_body") or "")
    aspect = str(spine.get("aspect") or "")
    if transit_body == "Neptune" and aspect in {"square", "conjunction", "opposition"}:
        return "az kelimeyle net çerçeve kurma"
    if transit_body == "Uranus" and aspect in {"trine", "sextile"}:
        return "yeni yöntemi ritme bağlama"
    if transit_body == "Saturn":
        return "sorumluluğu sade bir sisteme çevirme"
    return "daha gerçek bir yön hissi"


def _seed_for(value: str) -> int:
    raw = value if value else "seed"
    h = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return int(h[:8], 16)


def _snapshot_bodies_map(snapshot: Mapping[str, Any]) -> Dict[str, Dict[str, Any]]:
    bodies = snapshot.get("bodies")
    out: Dict[str, Dict[str, Any]] = {}

    if isinstance(bodies, Mapping):
        for key, value in bodies.items():
            if isinstance(value, Mapping):
                out[str(key).lower()] = dict(value)
        return out

    if isinstance(bodies, list):
        for item in bodies:
            if not isinstance(item, Mapping):
                continue
            name = str(item.get("name") or item.get("planet") or item.get("body") or "").strip()
            if not name:
                continue
            out[name.lower()] = dict(item)
    return out


def _cusp_for_house(house_cusps: Any, house: int) -> Optional[Dict[str, Any]]:
    if isinstance(house_cusps, Mapping):
        raw = house_cusps.get(str(house), house_cusps.get(house))
        if isinstance(raw, Mapping):
            return dict(raw)
    if isinstance(house_cusps, list):
        if 0 <= house < len(house_cusps) and isinstance(house_cusps[house], Mapping):
            return dict(house_cusps[house])
        idx = house - 1
        if 0 <= idx < len(house_cusps) and isinstance(house_cusps[idx], Mapping):
            return dict(house_cusps[idx])
    return None


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _render_track_variant(raw_pool: Any, seed: str, slot: str, vars_map: Mapping[str, str]) -> str:
    if not isinstance(raw_pool, Sequence) or isinstance(raw_pool, (str, bytes)):
        return ""
    pool = [str(x).strip() for x in raw_pool if str(x).strip()]
    if not pool:
        return ""
    idx = _seed_for(f"{seed}|{slot}") % len(pool)
    out = pool[idx]
    for key, value in vars_map.items():
        out = out.replace("{{" + key + "}}", str(value or ""))
    return out.strip()


def _build_planet_hook_tr(transit_body: str, aspect: str, target: str) -> str:
    planets = getattr(phrase_lib_tr, "PLANET_NATURE_TR", {})
    aspects = getattr(phrase_lib_tr, "ASPECT_FLAVOR_TR", {})
    targets = getattr(phrase_lib_tr, "TARGET_TONE_TR", {})

    p = planets.get(str(transit_body).strip(), {})
    a = aspects.get(str(aspect).strip().lower(), {})
    t_words = targets.get(str(target).strip().upper(), [str(target).strip() or "teması"])

    noun = (p.get("nouns") or ["tema"])[0]
    averb = (a.get("verbs") or ["açar"])[0]
    target_word = t_words[0]
    body = str(transit_body).strip() or "Bu etki"

    if str(aspect).strip().lower() in {"square", "opposition"}:
        return f"{body} bu dönemde {target_word} tarafında {noun} teması açıyor; o yüzden bu alan daha hassas ve daha görünür."
    if str(aspect).strip().lower() in {"trine", "sextile"}:
        return f"{body} {target_word} tarafında {noun} açıyor; bu da süreci daha akışkan ve daha kullanılabilir kılıyor."
    return f"{body} {target_word} tarafında {noun} temasını belirginleştiriyor."


def _final_polish_tr(text: str) -> str:
    out = str(text or "").replace("(", "").replace(")", "")
    for token in ("period", "exactish", "applying", "separating", "orb", "orb_deg"):
        out = out.replace(token, "")

    out = phrase_lib_tr.strip_tech_tokens(out)

    try:
        out = text_quality_tr.tr_normalize(out)
    except Exception:
        pass

    out = " ".join(out.split()).strip()
    return out


def _render_guardrail_issues(text: str) -> list[dict]:
    return [
        *find_forbidden_public_copy_issues(text, check_directives=False),
        *find_technical_leakage(text, surface="body"),
    ]
