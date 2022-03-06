#!/usr/bin/env python3

# TODO:
# * Allow user to save initial setup (particularly good game)
# * Allow user to load a saved game (simple pickle of seed w/ CLI options to load)

from typing import Tuple, List, Optional
import curses
import random
import sys
import time

ROWS = 8
COLS = 8
OPEN_SLOT = "_"
LIVE_SLOT = "O"

CURSES_KEY_MAP = {
    # north
    ord("k"): "n",
    curses.KEY_UP: "n",
    # south
    ord("j"): "s",
    curses.KEY_DOWN: "s",
    # west
    ord("h"): "w",
    curses.KEY_LEFT: "w",
    # east
    ord("l"): "e",
    curses.KEY_RIGHT: "e",
}

DIRECTIONAL_MAP = {
    "nw": (-1, -1),
    "n": (-1, 0),
    "ne": (-1, 1),
    "w": (0, -1),
    "e": (0, 1),
    "sw": (1, -1),
    "s": (1, 0),
    "se": (1, 1),
}


class Board:
    def __init__(self, rows: int, cols: int, seed: List[Tuple[int, int]]):
        self.rows = rows
        self.cols = cols
        self.seed = seed
        self.board = []
        self.is_over = False

        # Build a blank game board
        for _ in range(rows):
            self.board.append([OPEN_SLOT for _ in range(cols)])

        # Add the initial game state of living cells
        for coords in self.seed:
            i, j = coords
            self.board[i][j] = LIVE_SLOT

    def __repr__(self):
        s = ""
        for row in self.board:
            s += "".join(row) + "\n"

        return s

    def draw_board(self, curses_window):
        """Print board dynamically in-place using curses."""
        curses_window.erase()
        curses_window.addstr(str(self))
        curses_window.refresh()

    def get_neighbors(self, coords: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Looks at neighbors in 9x9 grid and returns i, j coords for non-null neighbors"""
        neighbors = []
        for direction in ["nw", "n", "ne", "w", "e", "sw", "s", "se"]:
            neighbor = self.get_inbound_coords(coords, direction)
            if neighbor:
                neighbors.append(neighbor)
        return neighbors

    def get_inbound_coords(
        self, coords: Tuple[int, int], directional: str
    ) -> Optional[Tuple[int, int]]:
        """Given coords and a direction, return a legal, in-bound set of coordinates or None.

        nw 0,  0 | n 0, 1 | ne  0, 2
          -1, -1 |  -1, 0 |    -1, 1
        ---------------------------
         w 1,  0 | c 1, 1 |  e  1, 2
           0, -1 |        |     0, 1
        ---------------------------
        sw 2,  0 | s 2, 1 | se  2, 2
           1, -1 |   1, 0 |     1, 1
        """

        i_mod, j_mod = DIRECTIONAL_MAP[directional]
        i, j = coords
        neighbor_coords = (i + i_mod, j + j_mod)

        if any(
            [
                neighbor_coords[0] < 0,
                neighbor_coords[1] < 0,
                neighbor_coords[0] > ROWS - 1,
                neighbor_coords[1] > COLS - 1,
            ]
        ):
            return None
        else:
            return neighbor_coords


def get_random_board_seed() -> List[Tuple[int, int]]:
    """Start the game with a random sequence."""
    elements = []
    for i in range(ROWS):
        for j in range(COLS):
            if random.choice([True, False]):
                elements.append((i, j))
    return elements


def get_user_board_seed(screen) -> List[Tuple[int, int]]:
    game = Board(ROWS, COLS, [])
    game.draw_board(screen)
    screen.move(0, 0)  # rest cursor after drawing blank board

    curr_xy = (0, 0)
    screen.nodelay(1)
    seed = []
    while True:
        x, y = curr_xy
        screen.move(x, y)

        key_pressed = screen.getch()  # No key == -1
        if key_pressed == -1:
            continue
        elif key_pressed == ord("\n"):
            break
        elif key_pressed == ord(" "):
            curr_val = chr(screen.inch(x, y))
            char_to_draw = OPEN_SLOT if curr_val == LIVE_SLOT else LIVE_SLOT
            screen.addstr(x, y, char_to_draw)
            screen.move(x, y)  # `addstr` advances cursor; put it back
            seed.append(coords)
        elif key_pressed > 0:
            coords = None
            direction = CURSES_KEY_MAP.get(key_pressed, "")
            if direction:
                coords = game.get_inbound_coords((x, y), direction)
            if coords:
                curr_xy = coords

    screen.nodelay(0)
    return seed


def init_board(screen, random_game=False):
    """Build an initial board based on ROWS / COLS"""
    if random_game:
        seed = get_random_board_seed()
    else:
        seed = get_user_board_seed(screen)
    return Board(ROWS, COLS, seed)


def main(curses_window):
    counter = 0
    game = init_board(curses_window)

    while not game.is_over:
        counter += 1
        game.is_over = True
        game.draw_board(curses_window)
        for i, row in enumerate(game.board):
            for j, item in enumerate(row):
                neighbors = [
                    game.board[x][y]
                    for x, y in game.get_neighbors((i, j))
                    if game.board[x][y] == LIVE_SLOT
                ]
                # A dead cell has exactly 3 neighbors => toggle to alive
                if item == OPEN_SLOT and len(neighbors) == 3:
                    game.board[i][j] = LIVE_SLOT
                    game.is_over = False
                # A living cell has 4 or more neighbors => toggle to dead
                elif item == LIVE_SLOT and len(neighbors) >= 4:
                    game.board[i][j] = OPEN_SLOT
                    game.is_over = False
                # When a living cell has 1 or fewer neighbors => toggle to dead
                elif item == LIVE_SLOT and len(neighbors) <= 1:
                    game.board[i][j] = OPEN_SLOT
                    game.is_over = False
        time.sleep(2)
    print("Game over. Your score is {}.".format(counter))
    time.sleep(10)
    sys.exit(0)


if __name__ == "__main__":
    curses.wrapper(main)
