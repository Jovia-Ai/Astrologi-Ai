from __future__ import annotations

import importlib.util
from pathlib import Path


def _load_script_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "export_natal_artifacts.py"
    spec = importlib.util.spec_from_file_location("export_natal_artifacts", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec is not None and spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_validate_artifacts_accepts_expected_birth_bundle() -> None:
    module = _load_script_module()

    module.validate_artifacts(["all"])


def test_export_artifacts_copies_exact_json_files(tmp_path: Path) -> None:
    module = _load_script_module()

    copied = module.export_artifacts(tmp_path, ["all"])

    assert [path.name for path in copied] == list(module.ARTIFACT_FILES.values())
    for variant, filename in module.ARTIFACT_FILES.items():
        source = module.resolve_artifact_paths()[variant]
        target = tmp_path / filename
        assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")


def test_main_print_paths_includes_expected_birth_datetime(capsys) -> None:
    module = _load_script_module()

    exit_code = module.main(["--print-paths"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "1996-12-28T07:10:00+02:00" in captured.out
    assert "natal_full_1996-12-28_07-10_istanbul.json" in captured.out
