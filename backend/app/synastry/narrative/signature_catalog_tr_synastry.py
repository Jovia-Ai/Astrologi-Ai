from __future__ import annotations

DOMAIN_LABEL_TR = {
    "identity": "kimlik",
    "mind_communication": "zihin ve iletişim",
    "relationships": "ilişki",
    "intimacy_depth": "mahremiyet ve yoğunluk",
    "private_inner_world": "iç dünya ve özel alan",
    "career_visibility": "görünürlük ve yön",
    "home_roots": "güven ve kök",
    "creativity_talent": "yaratıcılık ve ifade",
    "meaning_learning": "anlam ve ufuk",
    "social_future": "sosyal gelecek",
    "hidden_psyche": "iç dünya",
}

DOMAIN_ROOM_TR = {
    "identity": "kimlik ve duruş odası",
    "mind_communication": "zihin ve iletişim odası",
    "relationships": "ilişki odası",
    "intimacy_depth": "mahremiyet ve yoğunluk odası",
    "private_inner_world": "iç dünya ve özel alan odası",
    "career_visibility": "görünürlük ve yön odası",
    "home_roots": "güven ve kök odası",
    "creativity_talent": "yaratıcılık ve ifade odası",
    "meaning_learning": "anlam ve ufuk odası",
    "social_future": "sosyal gelecek odası",
    "hidden_psyche": "iç dünya odası",
}

DOMAIN_CHIP_TR = {
    "identity": "kimlik",
    "mind_communication": "iletişim",
    "relationships": "bağ",
    "intimacy_depth": "derinlik",
    "private_inner_world": "iç dünya",
    "career_visibility": "görünürlük",
    "home_roots": "güven",
    "creativity_talent": "yaratıcılık",
    "meaning_learning": "ufuk",
    "social_future": "sosyal alan",
    "hidden_psyche": "iç dünya",
}

MODE_COPY_TR = {
    "deep_familiar_but_triggering": {
        "label": "tanıdık ama yüksek yoğunluklu",
        "line": "tanıdıklık hissiyle yoran tarafı aynı anda büyütüyor",
        "chip": "tanıdık yoğunluk",
    },
    "growth_oriented_less_familiar": {
        "label": "daha geliştirici ama daha az tanıdık",
        "line": "alışılmış rahatlıktan çok değişim çağrısını öne çıkarıyor",
        "chip": "gelişim baskısı",
    },
    "familiar_growth_mix": {
        "label": "tanıdıklık ve gelişim aynı anda",
        "line": "hem yakın hissettiriyor hem de ilişkiyi yeni bir seviyeye çağırıyor",
        "chip": "tanıdık büyüme",
    },
    "high_charge_low_comfort": {
        "label": "yüksek yük ama düşük konfor",
        "line": "çekimi canlı tutarken duygusal maliyeti de yükseltiyor",
        "chip": "yüksek yük",
    },
    "comfort_forward": {
        "label": "konfor önde",
        "line": "önce tanıdıklık ve yerleşme hissi veriyor",
        "chip": "konfor",
    },
    "growth_forward": {
        "label": "gelişim önde",
        "line": "rahatlatmaktan çok geliştirmeye çalışıyor",
        "chip": "gelişim",
    },
    "mixed_activation": {
        "label": "karışık aktivasyon",
        "line": "aynı anda birden fazla alanı açtığı için düz bir çizgide ilerlemiyor",
        "chip": "karma etki",
    },
}

SHARED_THEME_COPY_TR = {
    "intense_magnetic_depth": {
        "line": "bu bağın ortak tonu çekimi derinlikle birleştiriyor",
        "chip": "manyetik derinlik",
    },
    "rooted_binding_pull": {
        "line": "bu bağın ortak tonu yerleşme ve bağ kurma isteğini büyütüyor",
        "chip": "köklenme",
    },
    "chemistry_forward_contact": {
        "line": "bu bağın ortak tonu önce kimyayı ve teması görünür kılıyor",
        "chip": "kimya",
    },
    "mixed_activation_field": {
        "line": "bu bağ tek bir duyguda toplanmıyor; aynı anda birkaç katmanda yaşanıyor",
        "chip": "karma alan",
    },
}

SUPPORT_COPY_TR = {
    "soft_attraction_plus_mental_flow": {
        "line": "çekimi taşıyan şey yalnız arzu değil, konuşma ve anlaşılma akışı da",
        "chip": "akıș",
    },
    "soft_attraction_buffer": {
        "line": "yumuşak çekim gerilimi çözmese de ilişkiye biraz nefes alanı açıyor",
        "chip": "yumuşak çekim",
    },
    "roots_and_home_support": {
        "line": "güven ve ev hissi bu bağı ayakta tutan ana dayanaklardan biri oluyor",
        "chip": "ev hissi",
    },
    "mental_flow_support": {
        "line": "bağı taşıyan şeylerden biri konuşabilmek ve birbirini anlayabilmek",
        "chip": "zihinsel akış",
    },
    "activation_without_clear_soft_buffer": {
        "line": "etki güçlü; ama onu yumuşatan doğal akış her zaman hazır değil",
        "chip": "ham etki",
    },
}

TENSION_COPY_TR = {
    "saturn_angular_pressure_plus_pluto_intensity": {
        "line": "ciddiyet baskısı ile yoğunluk aynı anda devreye giriyor",
        "chip": "baskı ve yoğunluk",
    },
    "pluto_intensity_plus_12th_pressure": {
        "line": "yoğunluk, geri çekilen duygular ve söylenmeyenler ilişkiye ekstra yük bindiriyor",
        "chip": "yoğun gizlilik",
    },
    "saturn_angular_pressure": {
        "line": "ilişkinin zorlayan tarafı sorumluluk, ağırlık ve baskı hissi",
        "chip": "baskı",
    },
    "12th_house_pressure": {
        "line": "ilişkinin zorlayan tarafı içe çekilme, belirsizlik ve saklı yükler",
        "chip": "12.ev baskısı",
    },
    "manageable_tension": {
        "line": "gerilim var; ama ilişkinin bütününü tek başına belirleyen ana kuvvet o değil",
        "chip": "yönetilebilir gerilim",
    },
}

BUNDLE_MECHANISM_COPY_TR = {
    "8th_personal_cluster": "Mahremiyet ve yakınlık alanı hızla merkeze yerleşiyor.",
    "roots_home_bundle": "Ev hissi, aidiyet ve yerleşme ihtiyacı belirginleşiyor.",
    "social_future_bundle": "Beraberlik duygusu sosyal alan, ortak çevre ve gelecek hissi üzerinden görünür oluyor.",
    "12th_pressure_bundle": "Söylenmeyenler ve geri çekilen duygular da sahnenin bir parçası oluyor.",
    "soft_attraction_bundle": "Yumuşak çekim hattı ilişkinin sert yerlerini bir süre taşıyabiliyor.",
    "pluto_personal_bundle": "Yoğunluk kolayca takıntı, güç ve kontrol temalarına kayabiliyor.",
    "saturn_angular_bundle": "Ciddiyet duygusu ile baskı hissi aynı anda artıyor.",
    "identity_activation_bundle": "Bu temas kişinin kendini algılama biçimine doğrudan değiyor.",
    "communication_bridge_bundle": "Konuşabilmek ve anlamlandırabilmek ilişkide gerçek bir taşıyıcı hat açıyor.",
    "nodal_fated_bundle": "Karşılaşma yön değiştirici ve kaderli hissedilebiliyor.",
}
