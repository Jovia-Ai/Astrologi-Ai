from app.transit.narrative.selection_evaluator import evaluate_daily_selection, evaluate_period_selection


def test_evaluate_daily_selection_reports_diversity_and_shadow_state() -> None:
    rows = [
        {
            "event_id": "evt_a",
            "house": 3,
            "aspect_mode": "polarity",
            "tone_face": "growth",
            "narrative_score": 0.7,
            "delta_salience_score": 0.12,
            "personalization_score": 0.03,
        },
        {
            "event_id": "evt_b",
            "house": 10,
            "aspect_mode": "flow",
            "tone_face": "shadow",
            "narrative_score": 0.6,
            "delta_salience_score": 0.08,
            "personalization_score": 0.01,
        },
    ]

    evaluation = evaluate_daily_selection(scored_rows=rows, daily_rows=rows, used_period_fallback=False)
    assert evaluation["selected_count"] == 2
    assert evaluation["house_diversity"] == 2
    assert evaluation["shadow_only_surface"] is False


def test_evaluate_period_selection_reports_roles_and_scores() -> None:
    selected = [
        {"event_id": "evt_spine", "domain": "career", "personalization_bonus": 0.03},
        {"event_id": "evt_support", "domain": "mind", "personalization_bonus": 0.01},
    ]
    evaluation = evaluate_period_selection(
        selected=selected,
        story_scores={"evt_spine": 0.84, "evt_support": 0.66},
        chapter_roles={"evt_spine": {"role": "builder"}, "evt_support": {"role": "peak"}},
    )
    assert evaluation["selected_count"] == 2
    assert evaluation["distinct_roles"] == 2
    assert evaluation["avg_story_score"] > 0.7
