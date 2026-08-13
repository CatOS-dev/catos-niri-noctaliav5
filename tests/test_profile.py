from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = "catos-niri-noctaliav5"
MANIFEST = ROOT / "usr/share/catdot/profiles" / PROFILE_ID / "profile.toml"
CONTENT = ROOT / "usr/share" / PROFILE_ID


class CatdotProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        catdot = os.environ.get("CATDOT_BIN")
        if not catdot:
            self.fail("CATDOT_BIN must point to the real catdot executable")
        self.catdot = Path(catdot)
        self.assertTrue(self.catdot.is_file(), self.catdot)

    def stage_profile(self, root: Path) -> tuple[Path, Path]:
        metadata = root / "usr/share/catdot/profiles" / PROFILE_ID
        content = root / "usr/share" / PROFILE_ID
        metadata.mkdir(parents=True)
        shutil.copy2(MANIFEST, metadata / "profile.toml")
        shutil.copytree(CONTENT, content)
        return root / "usr/share/catdot/profiles", content

    def fake_pacman(self, root: Path, packages: list[str]) -> Path:
        bindir = root / "bin"
        bindir.mkdir()
        installed = root / "installed-packages"
        installed.write_text("\n".join(packages) + "\n", encoding="utf-8")
        pacman = bindir / "pacman"
        pacman.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = -Qq ]; then cat \"$CATDOT_TEST_INSTALLED\"; exit 0; fi\n"
            "if [ \"$1\" = -S ]; then exit 0; fi\n"
            "printf 'unexpected pacman invocation: %s\\n' \"$*\" >&2\n"
            "exit 64\n",
            encoding="utf-8",
        )
        pacman.chmod(pacman.stat().st_mode | stat.S_IXUSR)
        sudo = bindir / "sudo"
        sudo.write_text("#!/bin/sh\nexec \"$@\"\n", encoding="utf-8")
        sudo.chmod(sudo.stat().st_mode | stat.S_IXUSR)
        return bindir

    def run_catdot(
        self,
        temp: Path,
        home: Path,
        profile_root: Path,
        bindir: Path,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "CATDOT_PROFILE_ROOT": str(profile_root),
                "CATDOT_TEST_INSTALLED": str(temp / "installed-packages"),
                "HOME": str(home),
                "XDG_STATE_HOME": str(home / ".local/state"),
                "PATH": f"{bindir}:/usr/bin:/bin",
            }
        )
        return subprocess.run(
            [str(self.catdot), *args],
            input="y\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_manifest_is_accepted_by_catdot_schema_four(self) -> None:
        manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(manifest["schema"], 4)
        self.assertIn("noctalia", manifest["packages"])

        with tempfile.TemporaryDirectory() as tmpdir:
            temp = Path(tmpdir)
            profile_root, _ = self.stage_profile(temp)
            result = subprocess.run(
                [str(self.catdot), "validate", str(profile_root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_select_and_update_preserve_runtime_machine_and_dconf_seeds(self) -> None:
        manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
        packages = manifest["packages"]
        managed = set(manifest["manage"])
        self.assertIn(".config/niri/noctalia/binds.kdl", managed)
        self.assertIn(".config/xdg-desktop-portal/niri-portals.conf", managed)
        self.assertNotIn(".config/niri/noctalia.kdl", managed)
        self.assertNotIn(
            ".config/niri/custom/catos-niri-noctaliav5/outputs.kdl", managed
        )
        self.assertNotIn(".config/dconf/user", managed)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp = Path(tmpdir)
            home = temp / "home"
            home.mkdir()
            profile_root, staged_content = self.stage_profile(temp)
            bindir = self.fake_pacman(temp, packages)

            selected = self.run_catdot(
                temp,
                home,
                profile_root,
                bindir,
                "select",
                PROFILE_ID,
                "--packages=verify",
            )
            self.assertEqual(selected.returncode, 0, selected.stderr)

            managed_niri = home / ".config/niri/config.kdl"
            managed_noctalia = home / ".config/noctalia/config.toml"
            managed_binds = home / ".config/niri/noctalia/binds.kdl"
            managed_portal = home / ".config/xdg-desktop-portal/niri-portals.conf"
            generated_niri_seed = home / ".config/niri/noctalia.kdl"
            output_seed = (
                home / ".config/niri/custom/catos-niri-noctaliav5/outputs.kdl"
            )
            dconf_seed = home / ".config/dconf/user"
            for path in (
                managed_niri,
                managed_noctalia,
                managed_binds,
                managed_portal,
                generated_niri_seed,
                output_seed,
                dconf_seed,
            ):
                self.assertTrue(path.is_file(), path)

            generated_niri_seed.write_text("runtime generated theme\n", encoding="utf-8")
            output_seed.write_text("user output layout\n", encoding="utf-8")
            dconf_seed.write_bytes(b"user dconf database")
            (staged_content / ".config/niri/config.kdl").write_text(
                managed_niri.read_text(encoding="utf-8") + "\n// managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/noctalia/config.toml").write_text(
                managed_noctalia.read_text(encoding="utf-8") + "\n# managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/niri/noctalia/binds.kdl").write_text(
                managed_binds.read_text(encoding="utf-8") + "\n// managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/xdg-desktop-portal/niri-portals.conf").write_text(
                managed_portal.read_text(encoding="utf-8") + "\n# managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/niri/noctalia.kdl").write_text(
                "profile generated theme update\n", encoding="utf-8"
            )
            (
                staged_content
                / ".config/niri/custom/catos-niri-noctaliav5/outputs.kdl"
            ).write_text(
                "profile output update\n", encoding="utf-8"
            )
            (staged_content / ".config/dconf/user").write_bytes(b"profile dconf update")

            updated = self.run_catdot(
                temp,
                home,
                profile_root,
                bindir,
                "update",
                PROFILE_ID,
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertIn("managed-update", managed_niri.read_text(encoding="utf-8"))
            self.assertIn("managed-update", managed_noctalia.read_text(encoding="utf-8"))
            self.assertIn("managed-update", managed_binds.read_text(encoding="utf-8"))
            self.assertIn("managed-update", managed_portal.read_text(encoding="utf-8"))
            self.assertEqual(
                generated_niri_seed.read_text(encoding="utf-8"),
                "runtime generated theme\n",
            )
            self.assertEqual(output_seed.read_text(encoding="utf-8"), "user output layout\n")
            self.assertEqual(dconf_seed.read_bytes(), b"user dconf database")

    def test_profile_has_no_display_manager_payload_or_hard_dependency(self) -> None:
        manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertNotIn("greetd", manifest["packages"])
        self.assertNotIn("noctalia-greeter", manifest["packages"])
        self.assertFalse((ROOT / "catos-niri-noctaliav5.install").exists())
        self.assertFalse(any("greetd" in str(path) for path in CONTENT.rglob("*")))

    def test_installed_profile_payload_is_readable_by_regular_users(self) -> None:
        files = [MANIFEST, *(path for path in CONTENT.rglob("*") if path.is_file())]
        for path in files:
            self.assertTrue(
                path.stat().st_mode & stat.S_IROTH,
                f"profile payload is not world-readable: {path.relative_to(ROOT)}",
            )


if __name__ == "__main__":
    unittest.main()
