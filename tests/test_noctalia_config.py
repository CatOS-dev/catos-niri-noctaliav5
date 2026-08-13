from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "usr/share/catos-niri-noctaliav5/.config/noctalia/config.toml"


class NoctaliaConfigTests(unittest.TestCase):
    def test_expected_builtin_templates_are_enabled(self) -> None:
        data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
        templates = data["theme"]["templates"]
        builtin_ids = templates["builtin_ids"]
        self.assertEqual(len(builtin_ids), len(set(builtin_ids)))
        self.assertEqual(
            set(builtin_ids),
            {"gtk3", "gtk4", "niri", "qt", "kitty", "starship"},
        )
        self.assertTrue(templates["enable_builtin_templates"])


if __name__ == "__main__":
    unittest.main()
