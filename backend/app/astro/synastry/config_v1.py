ASPECT_DEGREES = {
    "conjunction": 0,
    "sextile": 60,
    "square": 90,
    "trine": 120,
    "opposition": 180,
}

# Acilarin psikolojik dili: kareyi "yogunluk/friction" olarak normalize edecegiz.
ASPECT_COEFFS = {
    "conjunction": {"intensity": 1.00, "flow": 0.40, "friction": 0.40},
    "sextile": {"intensity": 0.70, "flow": 0.60, "friction": 0.20},
    "trine": {"intensity": 0.80, "flow": 0.75, "friction": 0.15},
    "square": {"intensity": 0.95, "flow": 0.20, "friction": 0.85},
    "opposition": {"intensity": 0.90, "flow": 0.25, "friction": 0.75},
}

# Gezegen agirliklari: "kisisel" daha yuksek, outer daha dusuk.
BODY_WEIGHTS = {
    "sun": 0.90,
    "moon": 1.10,
    "mercury": 0.70,
    "venus": 0.95,
    "mars": 1.00,
    "saturn": 0.90,
    "uranus": 0.55,
    "neptune": 0.55,
    "pluto": 0.65,
    "juno": 0.78,
    "node": 0.45,
    "vertex": 0.40,
    "asc": 0.85,
    "mc": 0.65,
}

# Orb aileleri (MVP). Outer-outer damping icin ayri kural engine'de.
BODY_FAMILY = {
    "sun": "lum",
    "moon": "lum",
    "mercury": "personal",
    "venus": "personal",
    "mars": "personal",
    "saturn": "social",
    "uranus": "outer",
    "neptune": "outer",
    "pluto": "outer",
    "juno": "point",
    "node": "point",
    "vertex": "point",
    "asc": "angle",
    "mc": "angle",
}

ORB_MAX_DEFAULT = 4.0
ORB_MAX_BY_PAIR_FAMILY = {
    # lum/personal daha genis, outer daha dar
    "lum_personal": 6.0,
    "lum_social": 5.0,
    "lum_outer": 3.0,
    "personal_personal": 5.0,
    "personal_social": 4.5,
    "personal_outer": 3.0,
    "social_social": 4.0,
    "social_outer": 3.0,
    "outer_outer": 2.0,
    "angle_personal": 4.0,
    "angle_lum": 4.5,
    "angle_outer": 2.5,
    "point_personal": 3.0,
    "point_lum": 3.0,
    "point_outer": 2.0,
}

# 4 kategori: bond, depth, spark, freedom
# category_map_factor: (body pair + aspect) => category factors
# MVP: bodyA/bodyB sirasiz (engine sorted key kullanir)
CATEGORY_MAP_FACTOR = {
    # --- Bond & guven: Moon/Venus/Saturn agirlikli
    "moon_venus_conjunction": {"bond": 1.00, "spark": 0.20},
    "moon_venus_trine": {"bond": 0.90},
    "moon_venus_sextile": {"bond": 0.70},
    "moon_saturn_conjunction": {"bond": 0.85, "depth": 0.25},
    "moon_saturn_square": {"bond": 0.70, "depth": 0.35},
    "venus_saturn_conjunction": {"bond": 0.80, "depth": 0.30},
    "venus_saturn_trine": {"bond": 0.85},
    "venus_saturn_square": {"bond": 0.65, "depth": 0.35},

    # --- Depth & donusum: Pluto/8.ev temasi (aspects)
    "moon_pluto_conjunction": {"depth": 1.00},
    "moon_pluto_opposition": {"depth": 0.95},
    "venus_pluto_conjunction": {"depth": 1.00, "spark": 0.35},
    "venus_pluto_square": {"depth": 0.90, "spark": 0.25},
    "mars_pluto_conjunction": {"depth": 0.85, "spark": 0.55},
    "sun_pluto_conjunction": {"depth": 0.80},

    # --- Spark & arzu: Mars/Venus + Mars/Moon
    "mars_venus_conjunction": {"spark": 1.00},
    "mars_venus_trine": {"spark": 0.85},
    "mars_venus_square": {"spark": 0.95},
    "mars_moon_conjunction": {"spark": 0.85, "bond": 0.25},
    "mars_moon_square": {"spark": 0.90, "bond": 0.15},

    # --- Freedom & bireysellik: Uranus temalari
    "uranus_moon_conjunction": {"freedom": 0.90, "spark": 0.20},
    "uranus_moon_opposition": {"freedom": 0.95},
    "uranus_venus_conjunction": {"freedom": 0.85, "spark": 0.35},
    "uranus_venus_square": {"freedom": 0.90, "spark": 0.25},
    "uranus_sun_conjunction": {"freedom": 0.85},

    # Genel fallback: Sun-Mercury gibi iletisim akisi (bond'a kucuk)
    "sun_mercury_trine": {"bond": 0.25},
    "mercury_mercury_conjunction": {"bond": 0.20},
}

# Risk kanallari (kategorilere karar degil, "golge kullanim" icin)
RISK_RULES = {
    "depth_control": {
        "moon_pluto_square": True,
        "moon_pluto_opposition": True,
        "venus_pluto_square": True,
        "venus_pluto_opposition": True,
        "mars_pluto_square": True,
        "mars_pluto_opposition": True,
        "saturn_pluto_conjunction": True,
        "saturn_pluto_square": True,
    },
    "spark_irrit": {
        "mars_mars_square": True,
        "mars_moon_square": True,
        "mars_mercury_square": True,
        "mars_venus_square": True,
    },
    "freedom_instab": {
        "uranus_moon_opposition": True,
        "uranus_venus_square": True,
        "uranus_sun_square": True,
        "uranus_mars_square": True,
    },
}

# Doyum parametreleri (raw sum -> 0..1)
K_BY_CATEGORY = {"bond": 1.4, "depth": 1.2, "spark": 1.3, "freedom": 1.1}
K_BY_RISK = {"depth_control": 1.0, "spark_irrit": 1.1, "freedom_instab": 1.0}

# Outer spam damp
OUTER_OUTER_DAMP = 0.15
ANGLE_HOUSE_DAMP_UNKNOWN_BIRTH_TIME = 0.42
