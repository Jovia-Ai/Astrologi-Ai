# v0.9a Identity/Career Debug Candidate Review

Scope:
- `v0.9a` debug-only composed semantic candidates
- families: `identity_route`, `career_route`
- `source_type = composed_semantic`
- `public_main/detail/support` rollout flags off

Validation status:
- public output remained unchanged on all reviewed charts when `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`, `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`, and `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`
- composed candidates appeared in `candidate_inventory` / ClusterPlan debug trace only
- no public surfaces changed

## Summary

Observed debug-only composed candidates:
- `identity_route`: generated on all 5 reviewed charts
- `career_route`: generated on 4 of 5 reviewed charts
- `career_route` did not generate on `buenos_aires_1980_09_09` under current `v0.9a` thresholds

Observed opportunity pattern:
- accepted golden `istanbul_1997_01_21`: no fallback opportunity, because public main is already exact/specific
- mixed charts with generic career fallback ownership: `fix06_grand_trine_flow`, `ankara_1993_06_10`, `dubai_1995_01_03`

## Chart Review

### Istanbul 1997 accepted golden

Raw signature:
`ASC Aries; MC Capricorn; Sun Aquarius 11H; Moon Cancer 3H; Mercury Capricorn 10H; Venus Capricorn 10H; Mars Libra 6H; Jupiter Capricorn 11H; Saturn Aries 12H; Uranus Aquarius 11H; Neptune Capricorn 10H; Pluto Sagittarius 8H`

Public output changed:
- `no`

`identity_route`
- `id`: `composed_identity_route_v0_9a`
- `subtype`: `direct_identity_spine`
- `domain`: `identity`
- `source_type`: `composed_semantic`
- `confidence`: `0.73`
- `confidence_tier`: `medium`
- `domain_reason`: `ASC route`, `chart ruler route`, `Sun identity anchor`, `1H amplification`
- `public_job`: `debug_only`
- `lived_scene`: `Kendini ortaya koyarken yönün daha hızlı belirginleşiyor; tavrın dışarıda daha çabuk okunuyor.`
- `lived_scene_atoms`: `ilk tepkiyi verirken kendi tonunun hemen görünmesi`; `bir grupta duruşunun hızlıca fark edilmesi`
- `gift`: `Kimlik çizgisini yalnız burç etiketiyle değil, gerçek yönlendiren rota üzerinden ayırabilmek.`
- `inner_tension`: `Dışarıda görünen tavrınla, kimliğini gerçekten hangi yaşam sahnesinde kurduğun her zaman aynı yerden çalışmayabilir.`
- `growth_direction`: `Kimlik hattını yükselen, yönetici gezegen ve Güneş arasında kurulan omurgadan okumak.`
- `evidence_trace`: `ASC Aries`, `Mars Libra 6H`, `Sun Aquarius 11H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`career_route`
- `id`: `composed_career_route_v0_9a`
- `subtype`: `public_voice`
- `domain`: `career`
- `source_type`: `composed_semantic`
- `confidence`: `0.94`
- `confidence_tier`: `high`
- `domain_reason`: `MC route`, `MC ruler involved`, `10H planet`
- `public_job`: `debug_only`
- `lived_scene`: `Dış dünyada yalnız ne yaptığın değil, nasıl konuştuğun ve nasıl konum aldığın da görünür hale geliyor.`
- `lived_scene_atoms`: `bir toplantıda söz aldığında tonunun ağırlık taşıması`; `ne söylediğinin dışarıdaki rolünü güçlendirmesi`
- `gift`: `Kariyer/public rol hattını MC ve yöneticisi üzerinden daha net ayırabilmek.`
- `inner_tension`: `Görünür olmak, sorumluluk almak ve gerçekten hangi rolde görünmek istediğin her zaman aynı hızla çözülmeyebilir.`
- `growth_direction`: `Kariyer hattını yalnız görünürlük olarak değil, MC-yönetici-10. ev rotası olarak okumak.`
- `evidence_trace`: `MC Capricorn`, `Saturn Aries 12H`, `Mercury/Venus/Neptune 10H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`composed_vs_generic_fallback_opportunities`
- none

### fix06_grand_trine_flow

Raw signature:
`ASC Cancer; MC Taurus; Sun Scorpio 4H; Moon Pisces 8H; Mercury Sagittarius 5H; Venus Scorpio 4H; Mars Sagittarius 5H; Jupiter Leo 1H; Saturn Virgo 2H; Uranus Scorpio 4H; Neptune Sagittarius 5H; Pluto Libra 3H`

Public output changed:
- `no`

`identity_route`
- `id`: `composed_identity_route_v0_9a`
- `subtype`: `private_identity_spine`
- `domain`: `identity`
- `source_type`: `composed_semantic`
- `confidence`: `0.71`
- `confidence_tier`: `medium`
- `domain_reason`: `ASC route`, `chart ruler route`, `Sun identity anchor`, `1H amplification`
- `public_job`: `debug_only`
- `lived_scene`: `Kimliğin dışarıya açık bir tavır kadar, içeride nasıl toparlandığın ve kendini nerede güvende hissettiğin üzerinden de kuruluyor.`
- `lived_scene_atoms`: `dışarıdan önce içeride toparlanman gereken an`; `kendini göstermeden önce geri çekilip yönünü ayarlaman`
- `evidence_trace`: `ASC Cancer`, `Moon Pisces 8H`, `Sun Scorpio 4H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`career_route`
- `id`: `composed_career_route_v0_9a`
- `subtype`: `strategic_role`
- `domain`: `career`
- `source_type`: `composed_semantic`
- `confidence`: `0.61`
- `confidence_tier`: `low`
- `domain_reason`: `MC route`, `MC ruler involved`, `10H planet`
- `public_job`: `debug_only`
- `lived_scene`: `Kariyer hattın yalnız görünürlük değil, nerede ve nasıl konum alacağını stratejik biçimde seçme ihtiyacını da taşıyor.`
- `lived_scene_atoms`: `hangi rolde görünmenin daha doğru olacağını tartman`; `dışarıdaki konumunu stratejik biçimde kurman`
- `evidence_trace`: `MC Taurus`, `Venus Scorpio 4H`, `Chiron Taurus 10H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`composed_vs_generic_fallback_opportunities`
- `composed_career_route_v0_9a` -> `career_career_like_career_career_visibility`

### ankara_1993_06_10

Raw signature:
`ASC Sagittarius; MC Libra; Sun Gemini 7H; Moon Pisces 3H; Mercury Cancer 7H; Venus Taurus 5H; Mars Leo 8H; Jupiter Libra 10H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 11H`

Public output changed:
- `no`

`identity_route`
- `id`: `composed_identity_route_v0_9a`
- `subtype`: `relational_identity_spine`
- `domain`: `identity`
- `source_type`: `composed_semantic`
- `confidence`: `0.8`
- `confidence_tier`: `high`
- `domain_reason`: `ASC route`, `chart ruler route`, `Sun identity anchor`
- `public_job`: `debug_only`
- `lived_scene`: `Kendini ortaya koyarken çoğu zaman tek başına değil, başkalarıyla kurduğun ilişki içinde pozisyon alıyorsun.`
- `lived_scene_atoms`: `bir ortama girerken karşı tarafın tonunu da hesaba katman`; `kendini anlatırken ilişki dengesini korumaya çalışman`
- `evidence_trace`: `ASC Sagittarius`, `Jupiter Libra 10H`, `Sun Gemini 7H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`career_route`
- `id`: `composed_career_route_v0_9a`
- `subtype`: `strategic_role`
- `domain`: `career`
- `source_type`: `composed_semantic`
- `confidence`: `0.61`
- `confidence_tier`: `low`
- `domain_reason`: `MC route`, `MC ruler involved`, `10H planet`
- `public_job`: `debug_only`
- `lived_scene`: `Kariyer hattın yalnız görünürlük değil, nerede ve nasıl konum alacağını stratejik biçimde seçme ihtiyacını da taşıyor.`
- `lived_scene_atoms`: `hangi rolde görünmenin daha doğru olacağını tartman`; `dışarıdaki konumunu stratejik biçimde kurman`
- `evidence_trace`: `MC Libra`, `Venus Taurus 5H`, `Jupiter Libra 10H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`composed_vs_generic_fallback_opportunities`
- `composed_career_route_v0_9a` -> `career_career_like_career_career_visibility`

### buenos_aires_1980_09_09

Raw signature:
`ASC Gemini; MC Pisces; Sun Virgo 3H; Moon Virgo 3H; Mercury Virgo 4H; Venus Leo 2H; Mars Scorpio 5H; Jupiter Virgo 3H; Saturn Virgo 4H; Uranus Scorpio 6H; Neptune Sagittarius 7H; Pluto Libra 4H`

Public output changed:
- `no`

`identity_route`
- `id`: `composed_identity_route_v0_9a`
- `subtype`: `private_identity_spine`
- `domain`: `identity`
- `source_type`: `composed_semantic`
- `confidence`: `0.67`
- `confidence_tier`: `medium`
- `domain_reason`: `ASC route`, `chart ruler route`, `Sun identity anchor`
- `public_job`: `debug_only`
- `lived_scene`: `Kimliğin dışarıya açık bir tavır kadar, içeride nasıl toparlandığın ve kendini nerede güvende hissettiğin üzerinden de kuruluyor.`
- `lived_scene_atoms`: `dışarıdan önce içeride toparlanman gereken an`; `kendini göstermeden önce geri çekilip yönünü ayarlaman`
- `evidence_trace`: `ASC Gemini`, `Mercury Virgo 4H`, `Sun Virgo 3H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`career_route`
- none generated under current `v0.9a` thresholds

`composed_vs_generic_fallback_opportunities`
- none

### dubai_1995_01_03

Raw signature:
`ASC Sagittarius; MC Virgo; Sun Capricorn 2H; Moon Aquarius 2H; Mercury Capricorn 2H; Venus Scorpio 12H; Mars Virgo 9H; Jupiter Sagittarius 1H; Saturn Pisces 3H; Uranus Capricorn 2H; Neptune Capricorn 2H; Pluto Scorpio 12H`

Public output changed:
- `no`

`identity_route`
- `id`: `composed_identity_route_v0_9a`
- `subtype`: `direct_identity_spine`
- `domain`: `identity`
- `source_type`: `composed_semantic`
- `confidence`: `0.78`
- `confidence_tier`: `medium`
- `domain_reason`: `ASC route`, `chart ruler route`, `Sun identity anchor`, `1H amplification`
- `public_job`: `debug_only`
- `lived_scene`: `Kendini ortaya koyarken yönün daha hızlı belirginleşiyor; tavrın dışarıda daha çabuk okunuyor.`
- `lived_scene_atoms`: `ilk tepkiyi verirken kendi tonunun hemen görünmesi`; `bir grupta duruşunun hızlıca fark edilmesi`
- `evidence_trace`: `ASC Sagittarius`, `Jupiter Sagittarius 1H`, `Sun Capricorn 2H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`career_route`
- `id`: `composed_career_route_v0_9a`
- `subtype`: `invisible_preparation_before_visibility`
- `domain`: `career`
- `source_type`: `composed_semantic`
- `confidence`: `0.63`
- `confidence_tier`: `low`
- `domain_reason`: `MC route`, `MC ruler involved`, `10H planet`
- `public_job`: `debug_only`
- `lived_scene`: `Görünür rolünden önce uzun bir hazırlık, perde arkası işleme ya da içerde kurma ihtiyacı çalışabiliyor.`
- `lived_scene_atoms`: `bir işi göstermeden önce içeride uzun süre hazırlaman`; `görünür olmadan önce zemini sessizce kurman`
- `evidence_trace`: `MC Virgo`, `Mercury Capricorn 2H`, `Chiron Virgo 10H`
- `public_eligibility`: `debug=true`, `detail=false`, `support=false`, `main=false`

`composed_vs_generic_fallback_opportunities`
- `composed_career_route_v0_9a` -> `career_career_like_career_career_visibility`

## No-Op Confirmation

Checked with:
- `ENABLE_NATAL_COMPOSED_SEMANTICS_V0_9=true`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_DETAIL_SUPPORT=false`
- `ENABLE_NATAL_COMPOSED_SEMANTICS_PUBLIC_MAIN=false`

Result:
- all reviewed charts kept identical public projection surfaces
- composed semantic candidates remained debug-only
- `public_main`, `public_support`, and `detail` routing did not change
