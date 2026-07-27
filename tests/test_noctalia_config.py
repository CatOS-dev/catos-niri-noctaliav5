from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "usr/share/catos-niri-noctaliav5/.config/noctalia/config.toml"


class NoctaliaConfigTests(unittest.TestCase):
    def test_builtin_template_ids_are_valid_toml_array(self) -> None:
        data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(
            data["theme"]["templates"]["builtin_ids"],
            ["gtk4", "gtk3", "qt", "niri"],
        )


if __name__ == "__main__":
    unittest.main()
