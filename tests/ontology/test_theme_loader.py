"""Tests for the deterministic theme ontology loader."""

from __future__ import annotations

import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
app_module = types.ModuleType("app")
app_module.__path__ = [str(ROOT / "backend" / "app")]
sys.modules["app"] = app_module

from app.ontology.theme_loader import load_theme_config


class ThemeLoaderTests(unittest.TestCase):
    def test_load_theme_config_reads_default(self) -> None:
        ontology = load_theme_config()
        self.assertEqual(ontology.max_themes_per_paragraph, 2)
        self.assertEqual(ontology.top_theme_share_cap, 0.6)
        self.assertEqual(len(ontology.themes), 13)

    def test_semantic_overlap_is_rejected(self) -> None:
        config = self._write_config(
            {
                "defaults": {
                    "max_themes_per_paragraph": 1,
                    "top_theme_share_cap": 0.6,
                },
                "caps": {"repetition_factor_cap": 0.2},
                "themes": {
                    "alpha": {
                        "question": "A",
                        "tension": "t_a",
                        "share_weight": 0.3,
                        "keywords": ["visibility"],
                    },
                    "beta": {
                        "question": "B",
                        "tension": "t_b",
                        "share_weight": 0.2,
                        "keywords": ["visibility"],
                    },
                },
            }
        )
        with self.assertRaisesRegex(ValueError, "Semantic overlap"):
            load_theme_config(config)

    def test_top_share_cap_violation(self) -> None:
        config = self._write_config(
            {
                "defaults": {
                    "max_themes_per_paragraph": 1,
                    "top_theme_share_cap": 0.4,
                },
                "caps": {"repetition_factor_cap": 0.2},
                "themes": {
                    "strong": {
                        "question": "A",
                        "tension": "t_a",
                        "share_weight": 0.5,
                        "keywords": ["pressure"],
                    }
                },
            }
        )
        with self.assertRaisesRegex(ValueError, "exceeds top_theme_share_cap"):
            load_theme_config(config)

    def _write_config(self, content: dict[str, object]) -> Path:
        fd, path = tempfile.mkstemp(suffix=".yaml")
        os.close(fd)
        temp_path = Path(path)
        temp_path.write_text(json.dumps(content))
        self.addCleanup(lambda: temp_path.unlink(missing_ok=True))
        return temp_path
