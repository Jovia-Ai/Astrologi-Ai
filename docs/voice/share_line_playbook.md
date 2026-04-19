# Share Line Playbook

Kullanıcı bir insight okur → hisseder → **screenshot alır** → paylaşır. Bu zincirin çalışması için her içgörünün başında **tek bir "alıntılık" satır** olması gerekir. Bu doküman o satırların nasıl yazılacağını, nerede saklandığını ve kalite testini tanımlar.

---

## 1) Yazım Kuralları (10 Madde)

| # | Kural | Neden |
|---|---|---|
| 1 | **6–12 kelime** | Ekran görüntüsünde okunabilir, parmak kaymaz |
| 2 | **Sen + şimdiki zaman** | "İnsanlar…" soğuk; "Sen…" samimi |
| 3 | **Tek iddia, tek cümle** | Bağlaç cümleyi dağıtır |
| 4 | **Somut davranış / his** | "Derin bağ" soyut; "yüzeyde duramıyorsun" somut |
| 5 | **Paradoks veya reframe** | Okuyan durur, düşünür, screenshot alır |
| 6 | **Sıfat cimri** | Her sıfat gücü düşürür |
| 7 | **Nokta ile bitir** | Soru ve üç nokta viral değil |
| 8 | **Astrolojik terim yok** | "Yükselenin" değil "insanlara ilk gösterdiğin sen" |
| 9 | **Utandırma yok, teşhis var** | Co-Star accusation tonunu, Chani reframe'iyle yumuşat |
| 10 | **Emoji / ünlem yok** | Mistik otorite kaybolur |

**11. Astrologi-spesifik kural:** Satırın arkasında bir yerleşim olduğu *sezilmeli* — "bu bana bir algoritma yazmıyor, haritamı okuyor" hissi.

---

## 2) Beş Yazım Formülü

### A — "Paradoks"
`[Sandığın şey] → [Gerçek]`
- "Kendini sakin sanıyorsun. Gerçekte çok duyuyorsun."
- "Güçlü olmak zorunda değilsin. Zaten güçlüsün."

### B — "İçsel Mekanik"
`[Nasıl çalıştığın] + [Neden]`
- "Önce düşünüyorsun, sonra var oluyorsun."
- "Güven gelmeden derinleşmiyorsun."

### C — "Reframe"
`[Gölge gördüğün şey] → [Aslında olan]`
- "Aşırı hassas değilsin — yüksek çözünürlüklüsün."
- "Kontrolcü değilsin. Sadece kaos seni yoruyor."

### D — "Teşhis + İzin"
`[Görülen] + [İzin cümlesi]`
- "Herkesi anlıyorsun. Bugün sadece kendini anla."

### E — "Kısa Bilge"
4–6 kelimelik mikro-aforizma
- "Direndiğin şey sana olmak istiyor."
- "Derinlik hız istemiyor."

---

## 3) Viral Test (Her Yeni Satır İçin)

Satırı yayınlamadan önce 4 soru:
- [ ] Ekran görüntüsünde okunabiliyor mu? (12 kelime altı)
- [ ] Arkadaşına atmak ister misin? ("Sana bak" hissi)
- [ ] Bir şey açığa çıkarıyor mu? (Genel değil, spesifik)
- [ ] Astrolojik terim sızıyor mu? (Sızıyorsa kes)

3/4 evet → yayınla. 4/4 → `quotable_tier: "A"`, öne çıkar.

---

## 4) Kod Yerleşimi

Bu satırlar **ayrı bir alan** olarak saklanır. Mevcut `headline_variants` / `title` / `one_liner` bozulmaz.

### Natal — [phrase_lib_tr_natal.py](../../backend/app/natal/narrative/phrase_lib_tr_natal.py)
Her thread variant dict'ine eklenen key:
```python
{
    "title": "Kimliğin nasıl çalışıyor?",
    "share_headline": "Önce düşünüyorsun, sonra var oluyorsun.",
    "one_liner": "...",
    "paragraph": "...",
}
```

### Transit — [transit_templates.v1.json](../../backend/app/transit/content/tr/transit_templates.v1.json)
```json
{
  "neptune.square.asc": {
    "headline_variants": ["Kimlikte sis"],
    "share_headline_variants": ["Bugün kim olduğun biraz buğulu. Bu geçecek."],
    "summary_variants": [...]
  }
}
```

### Synastry — [synastry_phrase_bank_tr.py](../../backend/app/synastry/narrative/synastry_phrase_bank_tr.py)
PAIR_SIGNATURE ve TOGETHER_FIELD şablonlarına:
```python
{
    "id": "pair_deep_warm_pull",
    "label": "Sıcak ama derin bağ",
    "share_line": "Bu bağ yüzeyde durmayı bilmiyor.",
    "one_liner": "...",
}
```

### L10N — [app_tr.arb](../../mobile/lib/l10n/app_tr.arb) / [app_en.arb](../../mobile/lib/l10n/app_en.arb)
Statik / rotasyonlu satırlar için `share_*` öneki:
- `shareHomeHeroRotation1..4` — Home hero alternatif promptları
- `shareAilaSignature1..4` — Aila sohbet imza satırları
- `shareStoryStudioIdentityClose` — Story Studio kart kapanışları
- `shareStoryStudioShadowClose`
- `shareStoryStudioGiftClose`
- `shareStoryStudioDriveClose`

---

## 5) Rotasyon Stratejisi

Bir surface birden fazla satır alıyorsa (ör. Home hero) **seed-stable random** kullan — aynı kullanıcı aynı gün aynı satırı görsün. Transit için zaten `pick_variant(seed, n)` mekanizması var; `share_headline_variants` dizisi de aynı seed ile seçilir.

---

## 6) Başlangıç Paketi (ilk 20 satır — commit'lendi)

### Story Studio kapanış mühürleri
1. "Sen bir performans değilsin. Bir ritim."
2. "Gölgen düşmanın değil — haritan."
3. "En iyi işini kimse görmediği yerde yapıyorsun."
4. "Önce düşünüyorsun, sonra var oluyorsun."
5. "Yüzeyde bağ kurmayı bilmiyorsun."

### Bond result
6. "Bu bağ yüzeyde durmayı bilmiyor."
7. "Kimyanız siz fark etmeden önce odaya fark ettiriyor."
8. "Aranızda acele yok — çünkü gitmiyor."
9. "Birlikte sakin olamıyorsunuz. Belki de olmamalısınız."

### Home / transit
10. "Bugün kim olduğun biraz buğulu. Bu geçecek."
11. "Direndiğin şey sana olmak istiyor."
12. "İstediğin şey ve yapman gereken şey bugün aynı masada."
13. "Bu hafta kalbin geri izliyor."
14. "Yanlış anlaşılmak için doğru hafta."

### Aila imza
15. "Bıraktığın zaman değil, bırakamadığın zaman kayıp ediyorsun."
16. "Eski kapıyı açmak, eskiye dönmek değildir."
17. "Haritada gördüğüm şey: sen zaten biliyorsun."
18. "Herkesi anlıyorsun. Bugün sadece kendini anla."

### Kariyer (yeni thread önerisi)
19. "Seni çağıran şey bağırmıyor. Fısıldıyor."
20. "Yorgun değilsin. Yanlış yerde çok iyisin."

---

## 7) Gelecek İş (bu fazda yapılmadı, liste)

- [ ] `career_calling`, `career_burnout`, `career_pivot` thread'lerini [phrase_lib_tr_natal.py](../../backend/app/natal/narrative/phrase_lib_tr_natal.py) içine ekle
- [ ] Natal `h11`, `h8`, `h3`, `h12` sub-variantlarına `share_headline` ekle (şu an sadece ana 6 variant dolduruldu)
- [ ] Transit havuzunu genişlet: `saturn.return`, `venus.retrograde`, `mercury.retrograde`, `jupiter.trine.any` için özel satır
- [ ] Mobile tarafında **paylaşım kartı widget'ı** — `share_headline`'ı büyük puntoda, altta küçük marka imzası
- [ ] Aila sohbet yanıtlarının sonuna **imza satırı** eklenmesi için AI prompt güncellemesi
- [ ] Home hero için `shareHomeHeroRotation*` key'lerinin rotasyonla gösterilmesi

---

## 8) Referans Notları

| App | Pattern | Bize Katkı |
|---|---|---|
| **Co-Star** | Accusation + imperative | Cesaret — ama şefkatle dengele |
| **The Pattern** | "You often feel…" uncanny | Bizde "sen…" şimdiki zaman yapısı |
| **Chani** | Reframe + refuse shame | Shadow safety template'imiz zaten buna yakın |
| **Sanctuary** | Permission-giving | "Bu senin hakkın" kalıpları |
| **Nebula** | Affirmation rhythm | Story Studio kapanış mühürleri |

---

Soru / öneri: ekip içinde bu dosya otorite. Yeni satır eklemeden önce 10 kurala + viral teste bak.
