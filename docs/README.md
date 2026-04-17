Test Setup

Install test dependencies:
```
cd backend
python -m pip install -r requirements-dev.txt
```

Run tests (from backend/):
```
PYTHONPATH=backend python -m pytest -q ../tests/engine/test_normalize_utils.py
PYTHONPATH=backend python -m pytest -q ../tests/engine
PYTHONPATH=backend python -m pytest -q ../tests/approval/test_narrative_snapshots.py
```

Mobile performance notes:

- `mobile_loading_tuning.md` documents home/profile loading invariants and the shared tuning file.
