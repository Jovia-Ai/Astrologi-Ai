from __future__ import annotations

from typing import Any, Dict, Set


def _norm(value: str) -> str:
    return (value or "").strip().lower()


def tags_for_marker(marker: Dict[str, Any]) -> Set[str]:
    """
    Marker objesinden intent scoring için 'tags' çıkarır.
    Bu tag’ler policy dosyasında kullanılır.
    """
    out: Set[str] = set()

    mid = _norm(str(marker.get("id") or ""))
    eid = _norm(str(marker.get("event_id") or marker.get("event") or ""))
    label = _norm(str(marker.get("label") or marker.get("title") or ""))

    hay = " ".join([mid, eid, label])

    if "venus" in hay or "venüs" in hay:
        out.add("venus")
    if "moon" in hay or "ay" in hay:
        out.add("moon")
    if "mercury" in hay or "merkür" in hay:
        out.add("mercury")
    if "jupiter" in hay or "jüpiter" in hay:
        out.add("jupiter")
    if "saturn" in hay or "satürn" in hay:
        out.add("saturn")
    if "mars" in hay:
        out.add("mars")
    if "neptune" in hay or "neptün" in hay:
        out.add("neptune")
    if "uranus" in hay or "uranüs" in hay:
        out.add("uranus")
    if "pluto" in hay:
        out.add("pluto")

    if "mc" in hay or "midheaven" in hay:
        out.add("mc")
        out.add("career")

    if "north node" in hay or "kuzey ay düğümü" in hay or "n.node" in hay:
        out.add("north_node")
        out.add("node")
    if "south node" in hay or "güney ay düğümü" in hay or "s.node" in hay:
        out.add("south_node")
        out.add("node")
    if "fortune" in hay or "part of fortune" in hay:
        out.add("fortune")
    if "vertex" in hay:
        out.add("vertex")
    if "chiron" in hay or "kiron" in hay:
        out.add("chiron")

    if "retro" in hay:
        out.add("retro")
        if "mercury" in out or "merkür" in hay:
            out.add("mercury_retro")
    if "dura" in hay or "station" in hay or "yön değişimi" in hay:
        out.add("station")
        if "mercury" in out or "merkür" in hay:
            out.add("mercury_station")
    if "voc" in hay or "void of course" in hay or "boşlukta" in hay:
        out.add("moon_voc")

    if "girişi" in hay or "ingress" in hay:
        if "ay" in hay or "moon" in hay:
            out.add("moon_ingress")
        if "venüs" in hay or "venus" in hay:
            out.add("venus_ingress")

    if ("ay boğa" in hay) or ("moon taurus" in hay):
        out.add("moon_taurus")
    if ("ay terazi" in hay) or ("moon libra" in hay):
        out.add("moon_libra")

    if "□" in hay or "square" in hay or "kare" in hay:
        out.add("square")
    if "☍" in hay or "opposition" in hay or "karşıt" in hay:
        out.add("opposition")
    if "□" in hay and ("moon" in out or "ay" in hay):
        out.add("moon_square")
    if "☍" in hay and ("moon" in out or "ay" in hay):
        out.add("moon_opposition")

    is_soft = (
        ("trine" in hay)
        or ("sextile" in hay)
        or ("△" in hay)
        or ("✶" in hay)
        or ("üçgen" in hay)
        or ("sekstil" in hay)
    )
    is_hard = (
        ("square" in hay)
        or ("opposition" in hay)
        or ("□" in hay)
        or ("☍" in hay)
        or ("kare" in hay)
        or ("karşıt" in hay)
    )

    if is_soft and ("moon" in out or "ay" in hay) and ("venus" in out or "venüs" in hay):
        out.add("moon_venus_soft")
    if is_soft and ("moon" in out or "ay" in hay) and ("neptune" in out or "neptün" in hay):
        out.add("moon_neptune_soft")
    if is_soft and ("venus" in out or "venüs" in hay) and ("neptune" in out or "neptün" in hay):
        out.add("venus_neptune_soft")

    if is_hard and ("moon" in out or "ay" in hay) and ("mars" in out or "mars" in hay):
        out.add("moon_mars_hard")
    if is_hard and ("moon" in out or "ay" in hay) and ("saturn" in out or "satürn" in hay):
        out.add("moon_saturn_hard")
    if is_hard and ("mars" in out or "mars" in hay) and ("venus" in out or "venüs" in hay):
        out.add("mars_venus_hard")
    if is_hard and ("venus" in out or "venüs" in hay) and ("saturn" in out or "satürn" in hay):
        out.add("venus_saturn_hard")
    if is_hard and ("mercury" in out or "merkür" in hay) and ("mars" in out or "mars" in hay):
        out.add("mercury_mars_hard")
    if is_hard and ("mercury" in out or "merkür" in hay) and ("neptune" in out or "neptün" in hay):
        out.add("mercury_neptune_hard")
    if is_hard and ("mars" in out) and ("saturn" in out or "satürn" in hay):
        out.add("mars_saturn_hard")

    if is_soft and ("mercury" in out or "merkür" in hay) and ("saturn" in out or "satürn" in hay):
        out.add("mercury_saturn_soft")
        out.add("contract_support")

    if is_soft and ("mercury" in out or "merkür" in hay) and ("jupiter" in out or "jüpiter" in hay):
        out.add("mercury_jupiter_soft")

    if is_soft and (("sun" in hay) or ("güneş" in hay)) and ("mc" in out or "midheaven" in hay):
        out.add("sun_mc_soft")

    return out
