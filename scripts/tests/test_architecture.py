from __future__ import annotations

import ast
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[1]


def imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


class ModuleBoundaryTest(unittest.TestCase):
    def test_runtime_context_has_no_cjk_io_dependency(self) -> None:
        modules = imported_modules(SCRIPTS_DIR / "config" / "runtime.py")
        self.assertFalse(any(module.startswith("scripts.cjk") for module in modules))

    def test_cjk_builder_has_no_config_resolver_dependency(self) -> None:
        modules = imported_modules(SCRIPTS_DIR / "cjk" / "builder.py")
        self.assertNotIn("scripts.config.resolver", modules)

    def test_config_base_has_no_browser_dependency(self) -> None:
        modules = imported_modules(SCRIPTS_DIR / "config" / "base.py")
        self.assertNotIn("scripts.in_browser", modules)

    def test_config_resolver_does_not_reexport_runtime_context(self) -> None:
        source = (SCRIPTS_DIR / "config" / "resolver.py").read_text(encoding="utf-8")
        self.assertNotIn("BuildRuntimeContext", source)
