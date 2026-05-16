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


def _skeleton(date, time, place, lat, lon, tz):
    return build_chart_skeleton(compute_natal_chart(
        date, time, place,
        birth_latitude=lat, birth_longitude=lon, birth_timezone=tz))


def _nairobi():
    return _skeleton("1962-01-07", "10:30", "Nairobi, KE",
                     -1.2921, 36.8219, "Africa/Nairobi")


def _helsinki():
    return _skeleton("1993-03-09", "08:50", "Helsinki, FI",
                     60.1699, 24.9384, "Europe/Helsinki")


def _dig(skel, planet):
    for r in skel["dignity_table"]:
        if r["planet"] == planet:
            return r
    return None


def test_pr2a_salience_scaffold_present_and_uncalibrated():
    skel = _skeleton_2019()
    assert skel["schema"] == "arc_chart_skeleton_v0_1"
    # Half-B now present on every dignity_table row.
    for row in skel["dignity_table"]:
        assert "salience" in row and isinstance(row["salience"], float)
        assert row["salience_tier"] in ("defining", "strong", "background")
    # The data itself must flag it as scaffold, not truth.
    assert skel["_salience_meta"]["_uncalibrated"] is True
    # Calibration (not the scaffold) is what stays corpus-blocked.
    joined = " ".join(skel["_deferred"])
    assert "salience CALIBRATION" in joined
    assert "salience_scoring" not in joined


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


def test_tightest_aspects_sorted_with_direction():
    skel = _skeleton_2019()
    aspects = skel["tightest_aspects"]
    assert aspects, "expected at least one aspect"
    orbs = [a["orb"] for a in aspects]
    assert orbs == sorted(orbs)
    # PR-1b: direction is the aspect_direction enum, not deferred.
    allowed = {"applying", "separating", "exact", None}
    assert all(a["direction"] in allowed for a in aspects)
    # Corpus-caught fix: only true planet-planet aspects — no angle-axis
    # self-pairs (Asc/Desc, MC/IC) or derived points (Vertex/Node).
    planets = {
        "sun", "moon", "mercury", "venus", "mars", "jupiter",
        "saturn", "uranus", "neptune", "pluto",
    }
    for a in aspects:
        assert str(a["a"]).lower() in planets
        assert str(a["b"]).lower() in planets


def test_dispositor_chains_present_and_well_formed():
    skel = _skeleton_2019()
    chains = {c["planet"]: c for c in skel["dispositor_chains"]}
    # Every classical planet present in the chart gets a chain entry.
    assert "Sun" in chains and "Saturn" in chains
    saturn = chains["Saturn"]
    # Saturn is in Capricorn (its own domicile) -> chain terminates fast.
    assert saturn["start_sign"] == "Capricorn"
    assert saturn["termination_reason"] in {
        "domicile", "loop_detected", "max_hops", "missing_data",
    }
    assert isinstance(saturn["primary_chain"], list)


def test_deferred_now_only_salience_calibration_and_chart_shape():
    skel = _skeleton_2019()
    deferred_joined = " ".join(skel["_deferred"])
    # PR-2a shipped the scaffold; only CALIBRATION stays corpus-blocked.
    assert "salience CALIBRATION" in deferred_joined
    assert "chart_shape" in deferred_joined
    assert "dispositor_chains" not in deferred_joined
    assert skel["dispositor_chains"], "dispositor_chains must be populated"


# --- PR-2a directional structural tests (UNCALIBRATED scaffold) ----------
# These do NOT assert calibrated correctness. They test whether the
# spec §2.2 formula's *direction* honours the locked "debilitated = loud"
# principle — and they document where it does NOT yet (the first
# calibration target, found structurally on 2 charts, by design).

def test_debilitated_but_role_supported_is_loud():
    """Nairobi Moon (Capricorn detriment) is a luminary in a 5-planet
    stellium → must NOT fall to background. Gold ranks it #2."""
    moon = _dig(_nairobi(), "Moon")
    assert moon["dignity"] == "detriment"
    assert moon["salience_tier"] == "defining", (
        f"Moon detriment should stay loud via luminary+stellium, "
        f"got {moon['salience_tier']} ({moon['salience']})")


def test_debilitated_chart_ruler_is_loud():
    """Helsinki Mercury (Pisces 12 detriment) is the chart ruler fused
    to the Sun → must read as defining. Gold ranks it #1."""
    merc = _dig(_helsinki(), "Mercury")
    assert merc["dignity"] == "detriment"
    assert merc["salience_tier"] == "defining", (
        f"debilitated chart ruler should be defining, got "
        f"{merc['salience_tier']} ({merc['salience']})")


def test_documented_gap_isolated_debilitated_planet_falls_to_background():
    """KNOWN UNCALIBRATED GAP (first calibration target): Helsinki Mars
    (Cancer fall) has no other role/stellium, so the §2.2 formula scores
    it 'background' — even though the gold ranks the Mercury/Venus/Mars
    debilitation cluster as the chart's #2 defining struggle. This is
    NOT a bug; it is the structural finding the 2-chart scaffold test was
    designed to surface: an isolated debilitated planet is not yet
    'loud'. Calibration (corpus) must add an affliction term."""
    mars = _dig(_helsinki(), "Mars")
    assert mars["dignity"] == "fall"
    assert mars["salience_tier"] == "background", (
        "if this no longer holds, the formula or weights changed — "
        "revisit the documented affliction-loudness gap")
