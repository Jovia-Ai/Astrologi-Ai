from __future__ import annotations

SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _deg_to_dms(deg: float) -> tuple[int, int]:
    # minutes only, no seconds (matches your output)
    d = int(deg)
    m = int(round((deg - d) * 60.0))
    if m == 60:
        d += 1
        m = 0
    return d, m


def format_lon(lon: float) -> tuple[str, float, str]:
    lon = lon % 360.0
    sign_idx = int(lon // 30.0)
    sign = SIGNS[sign_idx]
    deg_in_sign = lon - sign_idx * 30.0
    d, m = _deg_to_dms(deg_in_sign)
    return sign, deg_in_sign, f"{sign} {d}°{m:02d}′"
