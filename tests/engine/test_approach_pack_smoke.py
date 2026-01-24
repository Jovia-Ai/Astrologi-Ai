from pathlib import Path

from app.transit.interpret.interpretation_engine_v1 import ContentStore, _resolve_approach_text


def test_approach_pack_resolves() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    pack_path = repo_root / "backend" / "app" / "transit" / "content" / "tr" / "approach_pack.v1.json"
    pack = pack_path.read_text(encoding="utf-8")
    assert pack

    import json

    approach_pack = json.loads(pack)
    assert len(approach_pack) > 0

    store = ContentStore({}, {}, {}, {}, {}, approach_pack)
    text, _ref = _resolve_approach_text(
        event_id="tr.neptune.square.asc",
        transit_body="Neptune",
        polarity="hard",
        transit_style={"element": "water", "modality": "mutable"},
        target_style={"element": "earth", "modality": "cardinal"},
        content=store,
        include_debug=False,
    )
    assert text
