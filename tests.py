#!/usr/bin/env python3
import unittest
from life import Board

class NeighborhoodTests(unittest.TestCase):
    def test_get_neighbors(self):
        seed = [(0,2), (1,2), (2,2)]
        game = Board(8, 8, seed)
        self.assertFalse(game.is_over)

        target = game.get_live_neighbors((0,2))
        self.assertEqual(target, [(1, 2)])

        target = game.get_live_neighbors((1,2))
        self.assertEqual(target, [(0, 2), (2, 2)])

        target = game.get_live_neighbors((2,2))
        self.assertEqual(target, [(1, 2)])

        target = game.get_live_neighbors((1,1))
        self.assertEqual(target, [(0,2), (1, 2), (2, 2)])

        target = game.get_live_neighbors((1,3))
        self.assertEqual(target, [(0,2), (1, 2), (2, 2)])

    def test_get_inbound_coords_happy_path(self):
        seed = []
        game = Board(8, 8, seed)

        target = game.get_inbound_coords((1, 2), "n")
        self.assertEqual(target, (0, 2))

        target = game.get_inbound_coords((1, 2), "ne")
        self.assertEqual(target, (0, 3))

        target = game.get_inbound_coords((1, 2), "e")
        self.assertEqual(target, (1, 3))

        target = game.get_inbound_coords((1, 2), "se")
        self.assertEqual(target, (2, 3))

        target = game.get_inbound_coords((1, 2), "s")
        self.assertEqual(target, (2, 2))

        target = game.get_inbound_coords((1, 2), "sw")
        self.assertEqual(target, (2, 1))

        target = game.get_inbound_coords((1, 2), "w")
        self.assertEqual(target, (1, 1))

        target = game.get_inbound_coords((1, 2), "nw")
        self.assertEqual(target, (0, 1))

    def test_get_inbound_coords_board_edge(self):
        seed = []
        game = Board(8, 8, seed)

        for dir in ("nw", "n", "ne", "w"):
            target = game.get_inbound_coords((0, 0), dir)
            self.assertEqual(target, None, f"Failed on {dir}")

        for dir in ("sw", "s", "se", "e"):
            target = game.get_inbound_coords((7, 7), dir)
            self.assertEqual(target, None, f"Failed on {dir}")

if __name__ == "__main__":
    unittest.main()


# Rust WASM IMPL
# https://rustwasm.github.io/docs/book/game-of-life/rules.html