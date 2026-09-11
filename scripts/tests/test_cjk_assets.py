from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.cjk.assets import CJKBaseArchiveStore
from scripts.cjk.config import CJKBuildConfig, CJKOutputConfig, CJKSourceConfig
from scripts.config.base import CJKCommonBuildOptions, ResolvedCJKBuildEntry


class CJKBaseArchiveStoreTest(unittest.TestCase):
    def make_config(self, root: Path) -> CJKBuildConfig:
        return CJKBuildConfig(
            source=CJKSourceConfig(
                path=root / "source.ttf",
                masters={
                    100: {"wght": 100},
                    400: {"wght": 400},
                    800: {"wght": 800},
                },
            ),
            locale_name="CN",
            output=CJKOutputConfig(
                dir=root / "sources" / "cjk" / "cn",
                static_hash="static-cn.sha256",
                archive_name="cn-base-static.zip",
                variable_hash="variable-cn.sha256",
                variable_archive_name="cn-base-variable.zip",
            ),
        )

    def test_static_base_reuses_archive_from_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)
            archive = root / config.output.archive_name
            archive.write_bytes(b"local archive")
            store = CJKBaseArchiveStore("github.com")

            with (
                patch("scripts.cjk.assets.Path.cwd", return_value=root),
                patch.object(
                    store, "_install_local_archive", return_value=True
                ) as local,
                patch.object(store, "_install_static_archive") as remote,
            ):
                self.assertTrue(store.install_static_base("cn", config))

            self.assertEqual(local.call_args.args[0], archive)
            remote.assert_not_called()

    def test_variable_base_reuses_archive_from_project_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = self.make_config(root)
            config.output.dir.mkdir(parents=True)
            config.output.dir.joinpath(config.output.variable_hash).write_text(
                "0" * 64, encoding="utf-8"
            )
            archive = root / config.output.variable_archive_name
            archive.write_bytes(b"local archive")
            entry = ResolvedCJKBuildEntry(
                entry_id="cn",
                locale_name="CN",
                build_config=config,
                common_options=CJKCommonBuildOptions(),
                is_builtin=True,
                preset_id="cn",
            )
            store = CJKBaseArchiveStore("github.com")

            with (
                patch("scripts.cjk.assets.Path.cwd", return_value=root),
                patch.object(
                    store, "_install_local_archive", return_value=True
                ) as local,
                patch.object(store, "_install_variable_archive") as remote,
            ):
                self.assertTrue(store.ensure_variable_base(entry))

            self.assertEqual(local.call_args.args[0], archive)
            remote.assert_not_called()


if __name__ == "__main__":
    unittest.main()
