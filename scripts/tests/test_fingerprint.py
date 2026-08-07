from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.cache.digest import digest_tree
from scripts.cache.fingerprint import Fingerprint


class CanonicalDigestTest(unittest.TestCase):
    def test_file_name_is_part_of_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a.txt").write_text("abc")
            first = digest_tree(root)
            (root / "a.txt").rename(root / "b.txt")
            self.assertNotEqual(first, digest_tree(root))

    def test_file_boundaries_are_part_of_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "a").write_text("ab")
            (root / "b").write_text("c")
            first = digest_tree(root)
            (root / "a").write_text("a")
            (root / "b").write_text("bc")
            self.assertNotEqual(first, digest_tree(root))

    def test_symlink_hash_does_not_follow_target_outside_root(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "root"
            root.mkdir()
            target = Path(temporary) / "target.txt"
            target.write_text("first")
            (root / "link.txt").symlink_to(target)

            first = digest_tree(root)
            target.write_text("second")

            self.assertEqual(first, digest_tree(root))

    def test_fingerprint_is_order_independent_and_upstream_sensitive(self) -> None:
        first = Fingerprint().add_value("config", 1).add_upstream("source", "a")
        second = Fingerprint().add_upstream("source", "a").add_value("config", 1)
        changed = Fingerprint().add_value("config", 1).add_upstream("source", "b")
        self.assertEqual(first.digest(), second.digest())
        self.assertNotEqual(first.digest(), changed.digest())
