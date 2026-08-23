from __future__ import annotations

import unittest

from scripts.cjk.instances import map_weight_coordinate


class CJKInstanceWeightTest(unittest.TestCase):
    def test_map_weight_coordinate_preserves_axis_extremes_and_default(self) -> None:
        mapped = (
            map_weight_coordinate(100, 100, 400, 900, 200, 500, 800),
            map_weight_coordinate(400, 100, 400, 900, 200, 500, 800),
            map_weight_coordinate(900, 100, 400, 900, 200, 500, 800),
        )

        self.assertEqual(mapped, (200, 500, 800))

    def test_map_weight_coordinate_interpolates_each_side_of_default(self) -> None:
        self.assertEqual(map_weight_coordinate(250, 100, 400, 900, 200, 500, 800), 350)
        self.assertEqual(map_weight_coordinate(650, 100, 400, 900, 200, 500, 800), 650)
