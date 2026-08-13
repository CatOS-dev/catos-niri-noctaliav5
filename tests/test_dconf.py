from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DCONF_DIR = ROOT / "usr/share/catos-niri-noctaliav5/.config/dconf"
ALL_INI = DCONF_DIR / "all.ini"
USER_DB = DCONF_DIR / "user"


class DconfDefaultsTests(unittest.TestCase):
    def dump_user_database(self) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".config"
            dconf_dir = config_dir / "dconf"
            dconf_dir.mkdir(parents=True)
            shutil.copy2(USER_DB, dconf_dir / "user")
            env = os.environ.copy()
            env.update({"HOME": tmpdir, "XDG_CONFIG_HOME": str(config_dir)})
            return subprocess.run(
                ["dconf", "dump", "/"],
                check=True,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout

    @staticmethod
    def parse_dump(text: str) -> dict[tuple[str, str], str]:
        section = ""
        values: dict[tuple[str, str], str] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                continue
            key, value = line.split("=", 1)
            values[(section, key)] = value
        return values

    def test_text_export_matches_readable_binary_database(self) -> None:
        text_defaults = self.parse_dump(ALL_INI.read_text(encoding="utf-8"))
        binary_defaults = self.parse_dump(self.dump_user_database())
        self.assertEqual(text_defaults, binary_defaults)

    def test_dark_appearance_defaults_are_seeded(self) -> None:
        defaults = self.parse_dump(self.dump_user_database())
        self.assertEqual(
            defaults[("org/gnome/desktop/interface", "color-scheme")],
            "'prefer-dark'",
        )
        self.assertEqual(
            defaults[("org/gnome/desktop/interface", "cursor-theme")],
            "'Bibata-Modern-Classic'",
        )


if __name__ == "__main__":
    unittest.main()
