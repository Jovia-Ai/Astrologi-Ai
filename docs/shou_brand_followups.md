# SHOU Brand — Sonraki Yapılacaklar

Brand v2 migration sırasında listeye eklenmiş, şimdilik ertelenmiş işler.

## Highlight markup parser (backend + mobile köprüsü)

**Durum:** Manuel `ShouHighlight` widget'ı hazır ([mobile/lib/design/widgets/shou_highlight.dart](../mobile/lib/design/widgets/shou_highlight.dart)). Narrative section text'leri API'den düz string olarak geliyor — runtime'da hangi ifadelerin vurgulanacağı işaretli değil.

**Yapılacak:**
1. Backend narrative builder'larında (örn. `backend/app/engine/` içindeki profile narrative üretim katmanları) tagging konvansiyonu belirle:
   - `[[lime:bir kez daha geçiyorsun]]`
   - `[[lav:tam halini görmüyor]]`
   - `[[stone:ciddi görünür]]`
2. Mobile tarafta parser helper — `InlineSpan buildHighlightedText(String raw, ...)` → `RegExp(r'\[\[(lime|lav|stone):([^\]]+)\]\]')` yakalayıp `ShouHighlight.span(...)` ile değiştiren Text.rich üretir.
3. `_V8SectionCard`, `_V8DefenseCard`, `_V8FirstImpressionCard` ve diğer narrative kartlarında body metinlerini bu helper üzerinden render et.

**Öncelik:** Orta. Brand v2'nin en güçlü yeni hissi bu — narrative'in editorial kalitesini belirgin yükseltir. Ama API contract değişikliği gerektirdiği için bir sprint ayırmalı.

## Editorial italic display (splash + onboarding)

Brand v2 "Display XL" ve "Display LG Italic" sınıfları Fraunces 300 italic spec'inde. Şu an app-içi tüm metin Inter. Fraunces sadece splash / onboarding / marketing surface'leri için reserve.

**Yapılacak:**
- Splash tagline "Gökyüzü seni bekliyor." Fraunces 300 italic display variant'ı üzerinden render (şu an Inter olma ihtimali yüksek).
- Onboarding hero slide'larında aynı muamele.
- Mevcut typography factory'nin `display` (Fraunces) applier'ı korundu, kullanılmıyor — splash'te kullanmaya hazır.

**Öncelik:** Düşük-orta. Splash zaten brand-compliant görünüyor; yükseltme saatler sürer.

## Brand v2 bileşenlerinden eksikler

- **Story circle conic-gradient ring** — avatar'da dashed lime ring var, brand v2 `conic-gradient` ring öneriyor (aktif: lime, aynı dönem: lav, pasif: gri). Yeni widget gerekebilir.
- **Section header dot/line accent patterns** — `• SENİ NASIL ETKİLER` ve `— SECTION —` divider pattern'ları brand'de standardize; app'te ad hoc.
- **Data grid strip** (Önce / Sonra / Her zaman) — brand v2 bileşeni, app'te yok.

**Öncelik:** Düşük. Content geldikçe veya ilgili ekran refactor'da ele al.

## Hariç tutulanlar — ekleme

- **Amber (#E8A020)** ve **Deep Green (#3B6D11)** brand v2'de Career / Generel Transformation renkleri olarak tanımlı. Kullanıcı tercihi ile migration'a dahil edilmedi. Eğer ilerleyen aşamada renk kodlama genişletilmek istenirse bu iki tona `ProfileColors`'a dahil etme kararı tekrar açılabilir.
