"""TR prose library for deep_read slide flows.

Sibling to `phrase_lib_tr_profile.py`. That module serves
`render_block_template` (single-block emission, A/B/C/D modes,
domain-style block_ids). THIS module serves the deep_read slide-flow
emission shape: surface_role beats with hand-authored per-slide TR
prose.

S4a scope (matrix §5.2, this commit): canonical home for the
Phase-4 hidden/private slide PROSE. The actual builder still lives
in `app.meaning.composed_detail_renderer` as a thin adapter that
imports these constants — no render-machinery change in S4a.

S4b (deferred, separate later request): introduce a
`render_slide_flow(...)` helper near these constants; the per-role
entries evolve from a single `{title, body}` into a variant pool
(`{role: [{title, body}, ...]}`) to deliver chart-hash-seeded
variant rotation. Phase-4 hard invariants (B0-B5) are preserved
by S4a; S4b will preserve them too.

Discipline:
- This module is pure data. Zero imports beyond `__future__`.
- Prose strings are byte-identical to the original inline builder
  body. No editing during migration.
- Constant has exactly 5 entries — one per surface_role beat in the
  hidden/private deep_read profile. Adding entries (e.g. an inline
  origin_hint surface) is OUT OF SCOPE for S4a and would regress
  the Phase-4 authoring packet §4 opt-in-expandable contract.
"""

from __future__ import annotations


HIDDEN_PRIVATE_DEEP_READ_SLIDES_TR: dict[str, dict[str, str]] = {
    # private_scene · [ritim: sakin, içe dönük, yere basan]
    "private_scene": {
        "title": "Hemen göstermiyorsun",
        "body": (
            "Sen birine karşı bir şey hissettiğinde onu hemen "
            "gösterebilen yapıda değilsin. Önce içinde onun anlamını "
            "düşünür, senin için ne ifade ettiğini anlamaya "
            "çalışırsın. Bir şeyleri diğerlerine göre daha hassas "
            "ve derinden işlediğin için, düşünmeden söylediğinde "
            "karşı tarafın anlamayacağından ya da o hissin senin "
            "içindeki anlamının bozulacağından çekiniyor "
            "olabilirsin."
        ),
    },
    # hidden_mechanism · [ritim: kontrast — dış bakıştan içe + placement entegre]
    "hidden_mechanism": {
        "title": "Sessizliğin boşluk değil",
        "body": (
            "Bu yüzden dışarıdan biri seni bazen olduğundan sakin "
            "ya da biraz uzak bulabilir. Oysa içinde sakinlik "
            "değil, sürekli bir hareket var: sezgin, hayal gücün, "
            "bağlanma biçimin orada güçlü çalıştığı için bazen "
            "susarsın. Sezgilerinin \"şimdi\" dediği zamanı "
            "beklersin. 12. evinin Yay'da olması bu beklemeye "
            "bir yön daha katıyor — bir his sende anlam kazanmadan, "
            "daha büyük bir bütüne nasıl bağlandığını hissetmeden "
            "dışarı vermeyebilirsin."
        ),
    },
    # protective_pattern · [ritim: sessiz, dürüst, dramsız — konuşan ton]
    "protective_pattern": {
        "title": "Saklamak her zaman kaçmak değil",
        "body": (
            "Aslında senin yaptığın korkmak ya da kaçmak değil; "
            "bir şeyi koruma biçimindir. Onu başkasının sözüyle "
            "bozdurmadan, kendi içinde sahip çıkmak istersin. "
            "Doğru şekilde dışarı çıkmasını, karşı tarafın da "
            "onu öyle hissetmesini önemsersin. Yine de bir "
            "bedeli olabilir: her duyguyu tek başına taşımak yorar."
        ),
    },
    # gift_in_silence · [ritim: sıcak, açılan, cömert + light placement]
    "gift_in_silence": {
        "title": "İçten bağlılık sende güçlü çalışır",
        "body": (
            "Sevgi sende hemen tüketilmek istemez. Venüs'ün "
            "Yay'da işlemesi sevgine anlam arayan bir karakter "
            "veriyor: sevdiğin şeye dair sessiz ama derin bir "
            "bağlılık taşırsın. Güven oluştuğunda bu sıcaklık "
            "cömert, anlamlı ve uzun süre yaşayan bir bağa "
            "dönüşebilir — kolay söylenmeyen ama varlığı "
            "hissedilen bir şey."
        ),
    },
    # safe_visibility · [ritim: yatışan, eşik — imza bir kez]
    "safe_visibility": {
        "title": "İçeride taşımak ile gösterebilmek arasında",
        "body": (
            "Her şeyi hemen açmak zorunda değilsin. Ama içeride "
            "büyüttüğün şeyi güvendiğin bir yerde gerçek temasla "
            "buluşturabildiğinde, bu sende hem koruyan hem "
            "ilişkini daha gerçek kılan bir denge kurar. Sevgi "
            "sadece içeride taşınmaya devam etmek zorunda değil."
        ),
    },
}


HIDDEN_PRIVATE_DEEP_READ_SLIDE_ORDER: tuple[str, ...] = (
    "private_scene",
    "hidden_mechanism",
    "protective_pattern",
    "gift_in_silence",
    "safe_visibility",
)
