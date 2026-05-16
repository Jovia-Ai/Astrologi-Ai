"""ARC v0.1 — Layer 0 PR-1 acceptance: chart_skeleton vs 2019 oracle.

Deterministic regression. Proves the skeleton extraction surfaces the
chart spine the current packet-matching pipeline structurally buries —
with zero chart-specific hand authoring. See
docs/system/arc_v0_1_layer0_pr_plan.md (PR-4 oracle).
"""
from __future__ import annotations

from app.astro.chart_skeleton import build_chart_skeleton
from app.services.chart_service import compute_natal_chart


def _skeleton_2019():
    chart = compute_natal_chart(
        "2019-11-03", "23:40", "Istanbul, TR",
        birth_latitude=41.0082, birth_longitude=28.9784,
        birth_timezone="Europe/Istanbul",
    )
    return build_chart_skeleton(chart)


def _dignity(skel, planet):
    for row in skel["dignity_table"]:
        if row["planet"] == planet:
            return row
    return None


def test_skeleton_schema_and_no_salience_leak():
    skel = _skeleton_2019()
    assert skel["schema"] == "arc_chart_skeleton_v0_1_half_a"
    # Half B (salience) must NOT be present in PR-1.
    for row in skel["dignity_table"]:
        assert "salience" not in row
    assert "salience_scoring (PR-2, corpus-blocked)" in skel["_deferred"]


def test_luminaries_sun_scorpio_4th_moon_aquarius_6th():
    skel = _skeleton_2019()
    sun = skel["luminaries"]["sun"]
    moon = skel["luminaries"]["moon"]
    assert sun["sign"] == "Scorpio" and sun["house"] == 4
    assert sun["dignity"] == "peregrine"
    assert moon["sign"] == "Aquarius" and moon["house"] == 6
    assert moon["dignity"] == "peregrine"


def test_dignity_table_surfaces_the_two_biggest_current_misses():
    """The headline proof: dignity alone catches what selection buries."""
    skel = _skeleton_2019()
    jupiter = _dignity(skel, "Jupiter")
    saturn = _dignity(skel, "Saturn")
    # Jupiter domicile in 5th = the creative signature today invisible
    # (only a discovery_house_5h candidate, never surfaced).
    assert jupiter["sign"] == "Sagittarius" and jupiter["house"] == 5
    assert jupiter["dignity"] == "domicile"
    # Saturn domicile in 6th = the vocational signature today MISROUTED
    # into the relationship card.
    assert saturn["sign"] == "Capricorn" and saturn["house"] == 6
    assert saturn["dignity"] == "domicile"


def test_mars_libra_detriment_is_loud_not_filtered():
    skel = _skeleton_2019()
    mars = _dignity(skel, "Mars")
    assert mars["sign"] == "Libra" and mars["house"] == 3
    assert mars["dignity"] == "detriment"


def test_asc_mc_ruler_spine():
    skel = _skeleton_2019()
    asc = skel["asc_ruler_spine"]
    mc = skel["mc_ruler_spine"]
    # Leo Asc -> ruler Sun -> Sun in Scorpio, house 4
    assert asc["sign"] == "Leo"
    assert asc["ruler"] == "Sun"
    assert asc["ruler_sign"] == "Scorpio" and asc["ruler_house"] == 4
    # Aries MC -> ruler Mars -> Mars in Libra, house 3, detriment
    assert mc["sign"] == "Aries"
    assert mc["ruler"] == "Mars"
    assert mc["ruler_sign"] == "Libra" and mc["ruler_house"] == 3
    assert mc["ruler_dignity"] == "detriment"


def test_angular_planets_include_uranus_10th():
    skel = _skeleton_2019()
    angular = {a["planet"]: a for a in skel["angular_planets"]}
    assert "Uranus" in angular and angular["Uranus"]["house"] == 10
    assert "Sun" in angular and angular["Sun"]["house"] == 4
    # Mars in 3rd and Saturn in 6th are NOT angular.
    assert "Mars" not in angular
    assert "Saturn" not in angular


def test_sixth_house_stellium_detected():
    skel = _skeleton_2019()
    house_stelliums = {
        s["key"]: s for s in skel["stelliums"] if s["by"] == "house"
    }
    # Moon + Saturn + Pluto in the 6th = a real 3-planet stellium that
    # reinforces the Saturn-domicile-6th vocational spine.
    assert "6" in house_stelliums
    members = set(house_stelliums["6"]["planets"])
    assert {"Moon", "Saturn", "Pluto"}.issubset(members)


def test_tightest_aspects_sorted_and_applying_deferred():
    skel = _skeleton_2019()
    aspects = skel["tightest_aspects"]
    assert aspects, "expected at least one aspect"
    orbs = [a["orb"] for a in aspects]
    assert orbs == sorted(orbs)
    # applying/separating intentionally deferred in PR-1.
    assert all(a["applying"] is None for a in aspects)
