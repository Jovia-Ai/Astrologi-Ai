from __future__ import annotations

import hashlib
from typing import Any, Dict, List

from app.natal.narrative.micro_example_engine_tr import choose_micro_example

def _stable_int(s: str) -> int:
    return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16)


def pick_variant(seed: str, n: int) -> int:
    if n <= 0:
        return 0
    return _stable_int(seed) % n


def render(template: str, ctx: Dict[str, Any]) -> str:
    out = template
    for k, v in ctx.items():
        out = out.replace("{" + k + "}", "" if v is None else str(v))
    while "  " in out:
        out = out.replace("  ", " ")
    return out.strip()


THREAD_SKELETONS_TR: Dict[str, List[Dict[str, str]]] = {
    "identity_mechanics": [
        {
            "title": "Kimliğin nasıl çalışıyor?",
            "one_liner": "Kendini en çok düşünme biçimin ve ifade tarzın üzerinden kuruyorsun.",
            "paragraph": (
                "Yükselenin {asc_sign}; dışarıya daha kontrollü ve hedef odaklı çıkıyorsun. "
                "Ama asıl mekanizma yöneticin {asc_ruler}'ün {asc_ruler_house}. evde olması: "
                "kimliğin zihin ritmi ve iletişim kasın üzerinden güçleniyor. "
                "{loop_line} {micro}"
            ),
        },
        {
            "title": "Kimlik omurgan",
            "one_liner": "Netlik senin için lüks değil, güven hissi.",
            "paragraph": (
                "{asc_sign} yükselen seni sağlam durmaya çağırıyor. "
                "Yöneticin {asc_ruler} {asc_ruler_house}. evde olduğu için ben tarafı en çok söz ve karar düzeni üzerinden şekilleniyor. "
                "İyi gününde az cümleyle netlik, zor gününde fazla kontrol çalışabilir. "
                "{loop_line} {micro}"
            ),
        },
        {
            "title": "Duruş + Dil",
            "one_liner": "Duruşun güçlü; dilin doğru ayarlandığında etkisi iki kat.",
            "paragraph": (
                "Dışarıdan kararlı görünmen ({asc_sign}) doğal. "
                "Ama yöneticin {asc_ruler}'ün {asc_ruler_house}. evde olması seni nasıl söylediğin üzerinden sınar. "
                "Bazen en büyük dönüşüm cümleyi kısaltıp niyeti netleştirmektir. {micro}"
            ),
        },
        {
            "title": "Benlik sistemi",
            "one_liner": "Zihin-eylem-kontrol üçlüsü sende çok aktif.",
            "paragraph": (
                "Sende bir iç sistem çalışıyor: önce netleştiriyor, sonra harekete geçiyor, sonra tekrar kontrol ediyorsun. "
                "Bu döngü üretkenlik getirir ama dinlenmeyi zorlaştırabilir. "
                "Yükselen {asc_sign} ve {asc_ruler}'ün {asc_ruler_house}. ev vurgusu bu ritmi güçlendirir. {micro}"
            ),
        },
        {
            "title": "İfade kasın",
            "one_liner": "Kendini anlatma şeklin, kendini hissetme şeklini de değiştiriyor.",
            "paragraph": (
                "Kimliğin sadece nasıl göründüğün değil, nasıl anlattığınla da kuruluyor. "
                "{asc_ruler}'ün {asc_ruler_house}. ev vurgusu bazen aynı şeyi tekrar tekrar kontrol etmene neden olabilir. "
                "Burada hedef daha doğru cümle değil, daha dürüst cümle. {micro}"
            ),
        },
        {
            "title": "Netlik ihtiyacı",
            "one_liner": "Belirsizlik uzayınca içeride baskı artıyor.",
            "paragraph": (
                "Yükselen {asc_sign} belirsizliği sevmez. "
                "Yöneticin {asc_ruler} {asc_ruler_house}. evdeyken belirsizlik en çok iletişim ve karar anlarında görünür olur. "
                "Çözüm kontrolü artırmak değil, sınırı netleştirmektir. {micro}"
            ),
        },
    ],
    "relationships_depth": [
        {
            "title": "İlişkide eşik neresi?",
            "one_liner": "Bağ kurarken asıl eşik güven ve derinlik.",
            "paragraph": (
                "7. evin {dsc_sign}; yakınlık ve biz hissi önemli. "
                "Yöneticisi {r7} {r7_house}. evde olduğu için ilişki teması yüzeyde kalmaz, güven ve paylaşım üzerinden derinleşir. "
                "İyi kullanım adım adım açılmak, zor kullanım ya tamamen açılmak ya tamamen kapanmak. {micro}"
            ),
        },
        {
            "title": "Bağ kurma biçimin",
            "one_liner": "Yakınlık artınca güven testi devreye giriyor.",
            "paragraph": (
                "İlişkide sıcak ve koruyucu bir tarafın var ({dsc_sign}). "
                "Ama yöneticinin {r7_house}. ev vurgusu seni paylaşım ve sadakat ekseninde hassas yapar. "
                "Bu yüzden bunu söyleyeyim mi sorusu çoğu zaman güvende miyim sorusudur. {micro}"
            ),
        },
        {
            "title": "Duygusal derinlik",
            "one_liner": "Sende sevgi yüzey değil, kök ister.",
            "paragraph": (
                "7. evin {dsc_sign} olduğu için bağ kurmak istersin. "
                "Ama {r7}'nin {r7_house}. evde olması ilişkide tam temas aradığını gösterir. "
                "Küçük bir güven adımı senin için büyük bir eşiği geçmek olabilir. {micro}"
            ),
        },
        {
            "title": "Yakınlık ritmi",
            "one_liner": "Doğru ritimde ilerleyince ilişki çok güçlenir.",
            "paragraph": (
                "Senin ilişki ritmin hızlı yakınlık değil, güven kurdukça yakınlık. "
                "{r7}'nin {r7_house}. evde olması bağların derinleşmesini ister. "
                "Geri çekilmek doğal, ama tamamen kaybolmak yerine sinyal vermek daha iyi çalışır. {micro}"
            ),
        },
        {
            "title": "Güven dili",
            "one_liner": "İlişkide en çok netlik ve duygusal güven birleşince rahatlıyorsun.",
            "paragraph": (
                "Senin için güven sadece his değil, davranışta da görünmeli. "
                "7. ev {dsc_sign}; yöneticisi {r7} {r7_house}. evde. "
                "Söz-eylem tutarlılığı seni hızla rahatlatır ya da hızla soğutabilir. {micro}"
            ),
        },
        {
            "title": "Bağların derinleşmesi",
            "one_liner": "Sığ bağlar değil, belirsiz bağ yorar.",
            "paragraph": (
                "İlişkide sevgi kadar tanım da istersin. "
                "{r7_house}. ev vurgusu belirsizlikte içerden yorulmana neden olabilir. "
                "Çözüm bir anda her şeyi konuşmak değil, tek bir netlik cümlesiyle zemini kurmak. {micro}"
            ),
        },
    ],
    "career_visibility": [
        {
            "title": "Kariyerin nerede güçleniyor?",
            "one_liner": "Görünürlük kadar perde arkasında üretmek de seni besliyor.",
            "paragraph": (
                "MC'nin {mc_sign}: işte denge ve ilişki yönetimi öne çıkar. "
                "Yöneticisi {mc_ruler} {mc_ruler_house}. evde olduğunda en güçlü üretim çoğu zaman içeride olgunlaşır. "
                "Bu geri çekilme değil, hazırlık alanı. {micro}"
            ),
        },
        {
            "title": "Görünürlük ritmin",
            "one_liner": "Sahneye çıkınca etkilisin; ama önce içeride olgunlaştırıyorsun.",
            "paragraph": (
                "{mc_sign} MC sosyal zekayı ve doğru an hissini güçlendirir. "
                "{mc_ruler}'ün {mc_ruler_house}. evde olması seni perde arkasında derinleştirir: fikir, taslak, plan. "
                "Küçük sunumlar ve küçük paylaşımlarla görünürlüğü büyütmek sende daha iyi çalışır. {micro}"
            ),
        },
        {
            "title": "İş enerjin",
            "one_liner": "Kaliteyi yükseltmek imzan, ama bazen kendine fazla yük bindirebilirsin.",
            "paragraph": (
                "Kariyerde uyum ve denge arıyorsun ({mc_sign}). "
                "Ama {mc_ruler_house}. ev vurgusu iç standardı yükseltir; bazen kimse istemeden sen kendine daha fazlasını yüklersin. "
                "Burada ustalık mükemmeli değil, yayınlanabilir iyiyi seçmek. {micro}"
            ),
        },
        {
            "title": "Perde arkası güç",
            "one_liner": "Başarının bir kısmı sessizce kurulur.",
            "paragraph": (
                "{mc_ruler}'ün {mc_ruler_house}. ev yerleşimi görünür başarıdan önce görünmez emek ister. "
                "Herkesin hızına değil, kendi ritmine göre büyüdüğünde daha sağlam ilerlersin. "
                "Küçük ama somut adımlar senin güçlü ritmini kurabilir. {micro}"
            ),
        },
        {
            "title": "Kariyer sahnesi",
            "one_liner": "Doğru bağlamda parlıyorsun; yanlış bağlamda içe çekiliyorsun.",
            "paragraph": (
                "{mc_sign} MC seni bağlam kuran bir role çağırır. "
                "{mc_ruler_house}. ev filtresi anlam bulmadığın işte motivasyonu düşürebilir. "
                "Anlam netleşince ise tempo hızla toparlanır. {micro}"
            ),
        },
        {
            "title": "Görünür olma eşiği",
            "one_liner": "Görünürlük geldiğinde içeriden hazır mıyım sesi yükselebilir.",
            "paragraph": (
                "Bu sesin kaynağı çoğu zaman {mc_ruler_house}. ev vurgusudur: önce iç güven ister. "
                "Çözüm büyük bir çıkış değil, küçük ve düzenli bir görünürlük adımı. {micro}"
            ),
        },
    ],
    "direction_learning": [
        {
            "title": "Yön ve öğrenme teması",
            "one_liner": "Hareket enerjin ufuk genişletme ve öğrenme üzerinden çalışıyor.",
            "paragraph": (
                "Mars'ın {mars_house}. evde olması hedef koyduğunda öğrenme ve yön duygusu üzerinden hızlandığını gösterir. "
                "Ana risk dağılmak, ana güç tek bir hat seçip derinleşmek. "
                "Yön netleşince motivasyon kendiliğinden artar. {micro}"
            ),
        },
        {
            "title": "Yön kasın",
            "one_liner": "Nedenini bulunca çok hızlı ilerliyorsun.",
            "paragraph": (
                "{mars_house}. ev vurgusu seni anlam ve yönle besler. "
                "Bu yüzden sadece iş değil, yol hissi ararsın. "
                "Kısa bir yol haritası hızının çarpanı olur. {micro}"
            ),
        },
        {
            "title": "Öğrenerek büyüme",
            "one_liner": "Yeni bilgi sende sadece bilgi değil, özgüven de üretir.",
            "paragraph": (
                "Hareketin hevesle değil, yöntemle büyür. "
                "Öğrenme alanına yatırım yaptığında sadece beceri değil, iç sağlamlık da kazanırsın. {micro}"
            ),
        },
        {
            "title": "Tek hat stratejisi",
            "one_liner": "Aynı anda çok fazla yön açmak yorar; tek bir hat büyütür.",
            "paragraph": (
                "{mars_house}. ev ufuk demektir ama seçenek de artar. "
                "Sende en iyi çalışan şey tek bir hatta kalıp onu somutlaştırmaktır. {micro}"
            ),
        },
        {
            "title": "Uzak hedef",
            "one_liner": "Motivasyonun uzun vadeli anlam bulunca açılıyor.",
            "paragraph": (
                "{mars_house}. ev seni kısa vadeli telaştan çok uzun vadeli bir yöne çağırır. "
                "Bu yüzden önce yönü seçmek, hemen başlamak kadar önemlidir. {micro}"
            ),
        },
        {
            "title": "Yol haritası ihtiyacı",
            "one_liner": "Plan çıkınca rahatlıyor, plansızlıkta iç yük artıyor.",
            "paragraph": (
                "Plan senin için kontrol değil, güven. "
                "Kısa bir plan bile nereye gidiyoruz sorusunu kapatır ve zihin hızlanır. {micro}"
            ),
        },
    ],
}

THREAD_SKELETONS_TR.update(
    {
        "identity_mechanics:h11": [
            {
                "title": "Sosyal omurgan",
                "one_liner": "Kimliğin en çok çevren ve network'ün içinde şekilleniyor.",
                "paragraph": (
                    "Yükselenin {asc_sign}; dışarıya {asc_vibe} çıkman doğal. "
                    "Ama yöneticin {asc_ruler} {asc_ruler_house}. evde olduğu için 'ben' tarafın en çok {arena} üzerinden çalışıyor. "
                    "Bu yüzden bazen kendini tek başına değil, bir ekibin/çevrenin içinde daha net hissedersin: "
                    "rolün netleşince iç güvenin de artar. "
                    "{loop_line} {micro}"
                ),
            },
            {
                "title": "Ben + çevre",
                "one_liner": "Senin netliğin bazen 'kime bağlıyım / kimle ilerliyorum?' sorusuyla gelir.",
                "paragraph": (
                    "{asc_sign} yükselen seni dengede ve ölçülü tutar; ama {asc_ruler_house}. ev vurgusu, "
                    "kendini {arena} üzerinden tanımlamana neden olur. "
                    "İyi çalıştığında: doğru insanlarla doğru projeyi bağlarsın. "
                    "Zor çalıştığında: rol belirsiz kalınca motivasyon düşebilir. "
                    "{micro}"
                ),
            },
            {
                "title": "Network zekan",
                "one_liner": "İnsanları birbirine bağlamak sende doğal bir yetenek.",
                "paragraph": (
                    "Yöneticin {asc_ruler} {asc_ruler_house}. evdeyken, kimliğin 'bağ kurma' üzerinden güçlenir. "
                    "Sen çoğu zaman tek başına değil, doğru ekosistemde parlıyorsun. "
                    "Bu yüzden büyük sıçrama, bazen yeni bir yöntem değil; doğru bağlantıyı kurmaktır. "
                    "{micro}"
                ),
            },
            {
                "title": "Rol netliği",
                "one_liner": "En çok 'rolün net' olduğunda sakinleşiyorsun.",
                "paragraph": (
                    "Yükselen {asc_sign} belirsizliği uzatmayı sevmez. "
                    "Ama burada belirsizlik en çok {arena} sahnesinde görünür: 'Ben bu yapıda neredeyim?' "
                    "Ustalık, herkesi memnun etmek değil; rolünü tek cümleyle netleştirmektir. "
                    "{micro}"
                ),
            },
        ],
        "identity_mechanics:h3": [
            {
                "title": "Duruş + Dil",
                "one_liner": "Kimliğin, nasıl düşündüğün ve nasıl söylediğin üzerinden güçleniyor.",
                "paragraph": (
                    "Yükselenin {asc_sign}; dışarıya {asc_vibe} çıkarsın. "
                    "Yöneticin {asc_ruler} {asc_ruler_house}. evde olduğu için 'ben' tarafın en çok {arena} üzerinden kurulur. "
                    "Bazen en büyük dönüşüm, cümleyi kısaltıp niyeti netleştirmektir. "
                    "{loop_line} {micro}"
                ),
            },
            {
                "title": "Netlik ihtiyacı",
                "one_liner": "Belirsizlik uzayınca içerde yük artıyor.",
                "paragraph": (
                    "{asc_sign} yükselen belirsizliği sevmez. "
                    "{asc_ruler_house}. ev vurgusu, belirsizliği en çok {arena} anlarında görünür kılar. "
                    "Çözüm, daha çok düşünmek değil; sınırı daha iyi çizmek: 'Şu an bunu netleştirmiyorum.' "
                    "{micro}"
                ),
            },
            {
                "title": "İfade kasın",
                "one_liner": "Kendini anlatma şeklin, kendini hissetme şeklini de değiştiriyor.",
                "paragraph": (
                    "Kimliğin sadece 'nasıl göründüğün' değil; 'nasıl anlattığın'la da kuruluyor. "
                    "{asc_ruler} {asc_ruler_house}. evdeyken, zihin 'doğru cümleyi' aramaya yatkın olur. "
                    "Hedef daha 'doğru' cümle değil; daha 'dürüst' cümle. "
                    "{micro}"
                ),
            },
            {
                "title": "Zihin-eylem-kontrol",
                "one_liner": "Sende çalışan bir iç sistem var: netleştir, hareket et, toparla.",
                "paragraph": (
                    "{loop_line} "
                    "İyi çalıştığında hız ve ustalık getirir; zorlandığında kendine baskı artabilir. "
                    "Bu yüzden ritmini korumak, performansını doğrudan yükseltir. "
                    "{micro}"
                ),
            },
        ],
        "identity_mechanics:h12": [
            {
                "title": "Perde arkası benlik",
                "one_liner": "Kimliğin içeride olgunlaşınca dışarıda daha güçlü görünür.",
                "paragraph": (
                    "Yükselenin {asc_sign}; dışarıya {asc_vibe} çıkarsın. "
                    "Ama yöneticin {asc_ruler} {asc_ruler_house}. evde: 'ben' tarafın en çok {arena} içinde güçlenir. "
                    "Bu geri çekilme değil; hazırlık alanı. "
                    "Dışarı çıkmadan önce içerde olgunlaşman, sende kaliteyi artırır. "
                    "{micro}"
                ),
            },
            {
                "title": "İç güven",
                "one_liner": "Görünmeden önce içeride sağlamlaşmak istiyorsun.",
                "paragraph": (
                    "{asc_ruler_house}. ev vurgusu, seni iç dünyanda derinleştirir. "
                    "Bazen görünür olmak yaklaşınca 'hazır mıyım?' sesi yükselir; "
                    "çözüm büyük bir çıkış değil, küçük bir paylaşım adımıdır. "
                    "{micro}"
                ),
            },
            {
                "title": "Sessiz güç",
                "one_liner": "En büyük üretimin bir kısmı sessizce kurulur.",
                "paragraph": (
                    "Senin tarzın 'anında göster' değil; 'önce kur, sonra göster'. "
                    "{asc_ruler} {asc_ruler_house}. evdeyken bu doğal. "
                    "Küçük bir taslak, küçük bir prova; sonra net bir çıkış... bu sende iyi çalışır. "
                    "{micro}"
                ),
            },
            {
                "title": "İçeride büyütmek",
                "one_liner": "İçeride büyüttüğün şey dışarıya geç çıkabilir-bu tempo meselesi.",
                "paragraph": (
                    "{arena} sahnesi sende güçlü olduğunda, dışarıdan 'soğukkanlı' görünebilirsin. "
                    "Aslında içeride çok şey olur; sadece sen bunu hemen göstermeyi seçmezsin. "
                    "Kendine 'zaman' tanıdığında, dışarıdaki etki daha sağlam olur. "
                    "{micro}"
                ),
            },
        ],
        "identity_mechanics:hX": [
            {
                "title": "Kimlik omurgan",
                "one_liner": "Kimliğin, hangi alanda güçlendiğini bilince daha rahat akarsın.",
                "paragraph": (
                    "Yükselenin {asc_sign}; dışarıya {asc_vibe} çıkarsın. "
                    "Yöneticin {asc_ruler} {asc_ruler_house}. evde olduğu için 'ben' tarafın en çok {arena} üzerinden şekillenir. "
                    "Orayı netleştirdikçe hem kararların hem de duruşun güçlenir. "
                    "{micro}"
                ),
            },
            {
                "title": "Duruşun",
                "one_liner": "Duruşun güçlü; doğru bağlamda daha da etkili.",
                "paragraph": (
                    "{asc_sign} yükselen sana {asc_vibe} bir dış kabuk verir. "
                    "{asc_ruler_house}. ev vurgusu ise asıl ders alanını gösterir: {arena}. "
                    "Orada küçük bir ayar bile genel hayat hissini değiştirir. "
                    "{micro}"
                ),
            },
            {
                "title": "Netleşme kasın",
                "one_liner": "Netleşince hızlanıyorsun; net değilken içeri çekilmek doğal.",
                "paragraph": (
                    "Sende netlik bir 'kontrol' değil, bir 'güven' ayarı. "
                    "{arena} sahnesinde netlik kurdukça hem kendine hem başkalarına daha iyi akarsın. "
                    "{micro}"
                ),
            },
        ],
        "relationships_depth:h11": [
            {
                "title": "Arkadaşlıktan ilişkiye",
                "one_liner": "Bağların çoğu 'arkadaşlık / çevre' üzerinden kuruluyor.",
                "paragraph": (
                    "7. evin {dsc_sign}; ilişkide temas ve yakınlık istersin. "
                    "Ama yöneticisi {r7} {r7_house}. evde olduğu için, ilişki sahnen çoğu zaman {arena} üzerinden açılır: "
                    "arkadaşlıktan başlayan bağlar, birlikte üretmek, aynı çevrede büyümek... "
                    "Güven, 'biz aynı taraftayız' hissiyle hızlanır. "
                    "{micro}"
                ),
            },
            {
                "title": "Bağ kurma zeminin",
                "one_liner": "İlişkide 'aynı çevre / aynı hedef' teması güçlendiriyor.",
                "paragraph": (
                    "{r7} {r7_house}. evdeyken, ilişkilerinde sosyal bağlam belirleyici olur. "
                    "Birini 'arkadaş' olarak tanıyınca rahatlar; sonra yavaş yavaş derinleşirsin. "
                    "Ustalık: bağı belirsiz bırakmadan, rolü küçük bir cümleyle netleştirmek. "
                    "{micro}"
                ),
            },
            {
                "title": "İlişki + çevre",
                "one_liner": "Yakınlık, doğru ekip/çevrede daha rahat büyüyor.",
                "paragraph": (
                    "Senin ilişkilerin çoğu zaman tek kişilik bir hikaye değil; bir bağlamın içinde büyür. "
                    "{r7_house}. ev vurgusu, 'biz kimlerle birlikteyiz?' sorusunu önemli kılar. "
                    "Bu yüzden doğru çevre, doğru ilişkiyi daha hızlı görünür yapar. "
                    "{micro}"
                ),
            },
            {
                "title": "Sosyal güven",
                "one_liner": "Güven, bazen 'aynı planın içinde olmak'la gelir.",
                "paragraph": (
                    "İlişkide güven aradığında, bunu sadece duyguda değil; düzende de görmek istersin. "
                    "{r7}'nin {r7_house}. evde olması, ilişkiyi {arena} üzerinden sınar: plan, rol, birliktelik ritmi. "
                    "Küçük bir netlik cümlesi bile içini rahatlatır. "
                    "{micro}"
                ),
            },
        ],
        "relationships_depth:h8": [
            {
                "title": "Duygusal derinlik",
                "one_liner": "Sende sevgi yüzey değil; kök ister.",
                "paragraph": (
                    "7. evin {dsc_sign}; bağ kurmak istersin. "
                    "Ama yöneticisi {r7} {r7_house}. evde olduğunda, ilişki teması yüzeyde kalmaz; "
                    "güven, paylaşım ve duygusal derinlik üzerinden büyür. "
                    "İyi kullanımı: adım adım açılmak. Zor kullanımı: 'ya hep ya hiç'. "
                    "{micro}"
                ),
            },
            {
                "title": "Güven eşiği",
                "one_liner": "Yakınlık artınca 'güvende miyim?' testi devreye giriyor.",
                "paragraph": (
                    "{r7_house}. ev vurgusu, ilişkide en çok güven ve açıklık alanını büyütür. "
                    "Bu yüzden küçük bir sır paylaşmak bile senin için 'büyük bir adım' olabilir. "
                    "Kendini korumak doğal; ama sinyal vermek bağı koparmadan ilerletir. "
                    "{micro}"
                ),
            },
            {
                "title": "Yakınlık ritmi",
                "one_liner": "Senin ritmin hızlı yakınlık değil; güven kurdukça yakınlık.",
                "paragraph": (
                    "Sende ilişki, 'hız'la değil 'derinleşme'yle sağlamlaşır. "
                    "{r7} {r7_house}. evdeyken, belirsizlik yorar; netleşme rahatlatır. "
                    "Tek bir dürüst cümle çoğu zaman bütün sahneyi değiştirir. "
                    "{micro}"
                ),
            },
            {
                "title": "Tam temas ihtiyacı",
                "one_liner": "İlişkide en çok 'söz-eylem tutarlılığı' rahatlatıyor.",
                "paragraph": (
                    "{r7_house}. ev vurgusu, projeksiyonları değil gerçeği ister. "
                    "Bu yüzden tutarlılık gördüğünde hızlı sakinleşirsin; tutarsızlıkta hızlı yorulursun. "
                    "Çözüm: bir anda her şeyi konuşmak değil-tek bir netlik cümlesiyle zemin kurmak. "
                    "{micro}"
                ),
            },
        ],
        "relationships_depth:h3": [
            {
                "title": "İlişkide konuşma dili",
                "one_liner": "Bağların, nasıl konuştuğun ve nasıl anlaşıldığın üzerinden güçleniyor.",
                "paragraph": (
                    "7. evin {dsc_sign}; yakınlık istersin. "
                    "Ama yöneticisi {r7} {r7_house}. evde olduğu için, ilişkideki ana sahne {arena}: "
                    "mesaj, ton, konuşmayı kapatma biçimi... "
                    "Netlik kurduğunda bağ güçlenir; belirsizlik uzayınca yanlış okuma artabilir. "
                    "{micro}"
                ),
            },
            {
                "title": "Ton ayarı",
                "one_liner": "Bazen ilişkiyi değiştiren şey 'ne dediğin' değil 'nasıl söylediğin'.",
                "paragraph": (
                    "{r7_house}. ev vurgusu, ilişkiyi {arena} üzerinden hassaslaştırır. "
                    "Bu yüzden bir cümleyi yumuşatmak ya da kısaltmak, koca bir tartışmayı kapatabilir. "
                    "{micro}"
                ),
            },
            {
                "title": "Netlik ihtiyacı",
                "one_liner": "İlişkide belirsizlik uzayınca içerde yük artıyor.",
                "paragraph": (
                    "Sen belirsiz bağlarda yorulursun. "
                    "{arena} sahnesinde netlik kurduğunda, ilişki daha doğal akar. "
                    "Bir 'şu an buna girmiyorum' bile bazen en sağlıklı sınır olur. "
                    "{micro}"
                ),
            },
        ],
        "relationships_depth:h12": [
            {
                "title": "İlişkide gizli hassasiyet",
                "one_liner": "Yakınlık artınca içeri çekilmek bazen bir 'korunma' refleksi.",
                "paragraph": (
                    "7. evin {dsc_sign}; bağ kurmak istersin. "
                    "Ama yöneticisi {r7} {r7_house}. evdeyken, ilişki teması {arena} üzerinden içerde çalışır: "
                    "duyguyu önce içeride sindirmek istersin. "
                    "Çözüm, kaybolmak değil; küçük bir sinyal verip 'buradayım' demek. "
                    "{micro}"
                ),
            },
            {
                "title": "Perde arkası bağ",
                "one_liner": "Bağların içeride olgunlaşınca dışarıda daha sağlam olur.",
                "paragraph": (
                    "{r7_house}. ev vurgusu, ilişkiyi 'sessizce' büyütür. "
                    "Bazen dışarıdan yavaş görünür; ama içerde çok şey olur. "
                    "Küçük bir netlik adımı, ilişkiyi bir anda görünür kılabilir. "
                    "{micro}"
                ),
            },
            {
                "title": "Yakınlıkta ritim",
                "one_liner": "Senin ritmin: önce iç güven, sonra açıklık.",
                "paragraph": (
                    "Senin için güven, önce içeride kuruluyor. "
                    "{arena} sahnesinde kendine zaman verdiğinde, dışarıdaki temas da daha rahat olur. "
                    "Küçük bir paylaşım, büyük bir eşiği açabilir. "
                    "{micro}"
                ),
            },
        ],
        "relationships_depth:hX": [
            {
                "title": "Bağ kurma biçimin",
                "one_liner": "İlişkide en çok ritim ve netlik birleşince rahatlıyorsun.",
                "paragraph": (
                    "7. evin {dsc_sign}; bağ kurmak istersin. "
                    "Yöneticisi {r7} {r7_house}. evde olduğu için, ilişki teması en çok {arena} sahnesinde çalışır. "
                    "Küçük bir güven adımı, sende büyük bir rahatlama yaratabilir. "
                    "{micro}"
                ),
            },
            {
                "title": "İlişkide eşik",
                "one_liner": "Yakınlık artınca bir 'eşik' çalışıyor; adım adım ilerlemek iyi gelir.",
                "paragraph": (
                    "{r7_house}. ev vurgusu, ilişkide 'acele'yi sevmez. "
                    "Senin için en sağlıklı büyüme, küçük netlikler ve küçük temaslarla olur. "
                    "{micro}"
                ),
            },
        ],
        "career_visibility:h12": [
            {
                "title": "Perde arkası güç",
                "one_liner": "En güçlü üretimin çoğu zaman içeride olgunlaşıyor.",
                "paragraph": (
                    "MC'nin {mc_sign}: işte denge/ilişki yönetimi ve doğru bağlamı seçme yeteneğini güçlendirir. "
                    "Yöneticisi {mc_ruler} {mc_ruler_house}. evde olduğunda, üretimin bir kısmı {arena} içinde olgunlaşır. "
                    "Bu geri çekilme değil; hazırlık alanı. "
                    "{micro}"
                ),
            },
            {
                "title": "Görünür olma ritmin",
                "one_liner": "Sahneye çıkınca etkilisin; ama önce içerde olgunlaştırıyorsun.",
                "paragraph": (
                    "{mc_ruler_house}. ev vurgusu, 'hazır mıyım?' eşiğini yükseltebilir. "
                    "Çözüm büyük bir çıkış değil; küçük ve düzenli bir görünürlük adımı. "
                    "{micro}"
                ),
            },
            {
                "title": "Sessiz üretim",
                "one_liner": "Kimse bakmıyorken kurduğun şey, sonra çok güçlü görünür.",
                "paragraph": (
                    "Senin başarının bir kısmı görünmez emekten gelir. "
                    "{arena} sahnesinde bir işin taslağını kurup sonra doğru anda paylaşmak sende çok iyi çalışır. "
                    "{micro}"
                ),
            },
        ],
        "career_visibility:h11": [
            {
                "title": "Kariyerin sosyal sahnesi",
                "one_liner": "İşin, ekip ve network içinde büyüdüğünde hızlanıyor.",
                "paragraph": (
                    "MC'nin {mc_sign} sana 'doğru bağlam' sezgisi verir. "
                    "Yöneticisi {mc_ruler} {mc_ruler_house}. evdeyken, kariyer sahnen {arena}: ekip, topluluk, network. "
                    "İyi çalıştığında: insanları doğru yere bağlar, işi büyütürsün. "
                    "{micro}"
                ),
            },
            {
                "title": "İşbirliği gücü",
                "one_liner": "Tek başına değil; doğru işbirliğiyle parlıyorsun.",
                "paragraph": (
                    "{mc_ruler_house}. ev vurgusu, kariyerde 'birlikte üretim'i büyütür. "
                    "Bu yüzden doğru ekip, sana iki kat hız verir. "
                    "{micro}"
                ),
            },
            {
                "title": "Network kaldıracı",
                "one_liner": "Küçük bir bağlantı, büyük bir kapı açabilir.",
                "paragraph": (
                    "{arena} sahnesi güçlü olduğunda, kariyerde bazen bir 'tek bağlantı' her şeyi hızlandırır. "
                    "Ustalık: herkese yetişmek değil; doğru bağlantıyı doğru anda kurmak. "
                    "{micro}"
                ),
            },
        ],
        "career_visibility:h10": [
            {
                "title": "Doğrudan sahne",
                "one_liner": "Görünürlük sende ana sahne; ortaya koyduğun iş konuşur.",
                "paragraph": (
                    "MC'nin {mc_sign} yön duygunu güçlendirir. "
                    "Yöneticisi {mc_ruler} {mc_ruler_house}. evde olduğunda, kariyer sahnen doğrudan {arena}. "
                    "Bu yüzden işte en büyük büyüme, yaptığın işi dışarı taşımakla gelir. "
                    "{micro}"
                ),
            },
            {
                "title": "Çıktı kası",
                "one_liner": "Senin için başarı: üretmek ve görünür kılmak.",
                "paragraph": (
                    "{mc_ruler_house}. ev vurgusu, hedefleri somutlaştırır. "
                    "Mükemmelini beklemek yerine 'yayınlanabilir iyi'yi seçtiğinde çok hızlanırsın. "
                    "{micro}"
                ),
            },
        ],
        "career_visibility:hX": [
            {
                "title": "Kariyerin nerede güçleniyor?",
                "one_liner": "Başarı, doğru bağlamı seçince daha doğal akıyor.",
                "paragraph": (
                    "MC'nin {mc_sign} sana denge ve yön duygusu verir. "
                    "Yöneticisi {mc_ruler} {mc_ruler_house}. evde olduğu için kariyer sahnen {arena} üzerinden çalışır. "
                    "Orada küçük bir netlik adımı bile performansını büyütür. "
                    "{micro}"
                ),
            },
            {
                "title": "Görünürlük ayarı",
                "one_liner": "Görünürlük senin için bir ayar: dozunu doğru kurunca parlıyorsun.",
                "paragraph": (
                    "{arena} sahnesinde ritim kurduğunda, kariyerde de daha rahat görünür olursun. "
                    "Küçük adımlar, büyük baskıyı azaltır. "
                    "{micro}"
                ),
            },
        ],
    }
)


def build_loop_line(dominant_loops: List[Dict[str, Any]]) -> str:
    if not dominant_loops:
        return ""
    loop = dominant_loops[0]
    planets = loop.get("planets") or []
    if len(planets) >= 3:
        return f"Sende {planets[0]}-{planets[1]}-{planets[2]} arasında tekrar eden bir iç döngü var; iyi çalıştığında hız ve ustalık getirir."
    signature = str(loop.get("signature") or "").strip()
    if signature:
        return f"Sende tekrar eden bir iç döngü var ({signature}); iyi çalıştığında hız ve ustalık getirir."
    return ""


def micro_for(
    seed: str,
    arena_house: int,
    mode: str,
    tone_planets: List[str],
    valence: str,
) -> str:
    return choose_micro_example(
        seed=seed,
        arena_house=arena_house,
        mode=mode,
        tone_planets=tone_planets,
        valence=valence,
    )


def pick_micro(domain: str, seed: str) -> str:
    """
    Backward-compatible wrapper for existing callers.
    """
    mapping = {
        "identity": (1, ["Sun"]),
        "relationships": (7, ["Venus"]),
        "career": (10, ["Saturn"]),
        "direction": (9, ["Mars"]),
    }
    house, tones = mapping.get(domain, (1, ["Sun"]))
    return micro_for(
        seed=seed,
        arena_house=house,
        mode="neutral",
        tone_planets=tones,
        valence="growth",
    )


def render_thread_tr(thread_id: str, ctx: Dict[str, Any], seed: str) -> Dict[str, str]:
    variants = THREAD_SKELETONS_TR.get(thread_id, [])
    if not variants and ":" in thread_id:
        base = thread_id.split(":", 1)[0]
        variants = THREAD_SKELETONS_TR.get(f"{base}:hX", [])
    if not variants:
        return {"title": "", "one_liner": "", "paragraph": ""}

    i = pick_variant(seed + ":" + thread_id, len(variants))
    tpl = variants[i]
    return {
        "title": render(tpl["title"], ctx),
        "one_liner": render(tpl["one_liner"], ctx),
        "paragraph": render(tpl["paragraph"], ctx),
    }
