#!/usr/bin/env python3

# TODO:
# * Save a game, load it from disk
# * Pass in options to choose random vs user
# * Maybe allow a user to modify a randomly seeded board
# * Take a look at the types
# * Actually check out type hints.

from typing import Tuple, List, Optional
import curses
import random
import sys
import time

DEAD = "_"
ALIVE = "█"

KEY_MOVEMENT_MAP = {
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
        self.next_board = []
        self.is_over = False

        # Build a blank game board
        for _ in range(rows):
            self.board.append([DEAD for _ in range(cols)])

        # Add the initial game state of living cells
        for coords in self.seed:
            i, j = coords
            self.board[i][j] = ALIVE

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
        curses.curs_set(0)

    def get_live_neighbors(self, coords: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Looks at neighbors in 9x9 grid and returns i, j coords for all live neighbors"""
        neighbors = []

        for direction in ["nw", "n", "ne", "w", "e", "sw", "s", "se"]:
            neighbor = self.get_inbound_coords(coords, direction)
            if neighbor:
                i, j = neighbor
                if self.board[i][j] == ALIVE:
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
                neighbor_coords[0] > self.rows - 1,
                neighbor_coords[1] > self.cols - 1,
            ]
        ):
            return None
        else:
            return neighbor_coords


def get_rows_cols(screen) -> Tuple[int, int]:
    """Get the rows (height) and cols (width) of the provided screen.

    Be sure we trim one element from each dimension as addch/addstr will
    advance the cursor past what was printed.
    """
    rows, cols = screen.getmaxyx()
    return rows - 1, cols - 1


def get_random_board_seed(screen) -> List[Tuple[int, int]]:
    """Start the game with a random sequence."""
    elements = []
    rows, cols = get_rows_cols(screen)
    for i in range(rows):
        for j in range(cols):
            if random.choice([True, False]):
                elements.append((i, j))
    return elements, rows, cols


def get_user_board_seed(screen) -> List[Tuple[int, int]]:
    """Display blank board, let user seed initial values via curses."""
    rows, cols = get_rows_cols(screen)
    game = Board(rows, cols, [])
    game.draw_board(screen)
    curses.curs_set(2)
    screen.move(0, 0)  # rest cursor after drawing blank board

    curr_xy = (0, 0)
    screen.nodelay(1)
    seed = []
    while True:
        x, y = curr_xy
        screen.move(x, y)

        key_pressed = screen.getch()  # ascii code of key; -1 if none
        if key_pressed == ord("\n"):
            break
        elif key_pressed == ord(" "):
            curr_val = chr(screen.inch(x, y))
            char_to_draw = DEAD if curr_val == ALIVE else ALIVE
            screen.addstr(x, y, char_to_draw)
            screen.move(x, y)  # `addstr` advances cursor; put it back
            seed.append(curr_xy)
        elif direction := KEY_MOVEMENT_MAP.get(key_pressed):
            coords = game.get_inbound_coords((x, y), direction)
            if coords:
                curr_xy = coords

    screen.nodelay(0)
    curses.curs_set(0)
    return seed


def seed_initial_board(screen, random_game=False):
    """Build an initial board based on existing terminal size"""
    if random_game:
        seed, rows, cols = get_random_board_seed(screen)
    else:
        seed, rows, cols = get_user_board_seed(screen)
    return Board(rows, cols, seed)


def main(curses_window):
    counter = 0
    is_random = len(sys.argv) > 1 and sys.argv[1] == "random"
    game = seed_initial_board(curses_window, random_game=is_random)

    while not game.is_over:
        counter += 1
        game.is_over = True
        game.draw_board(curses_window)

        # Build the off-screen board to compute live/dead cells
        game.next_board = []
        for _ in range(game.rows):
            game.next_board.append([DEAD for _ in range(game.cols)])

        for i, row in enumerate(game.board):
            for j, item in enumerate(row):
                num_neighbors = len(
                    [
                        game.board[x][y]
                        for x, y in game.get_live_neighbors((i, j))
                        if game.board[x][y] == ALIVE
                    ]
                )

                # A dead cell has exactly 3 neighbors => toggle to alive
                if item == DEAD and num_neighbors == 3:
                    game.next_board[i][j] = ALIVE
                    game.is_over = False
                # A living cell has 4 or more neighbors => toggle to dead
                elif item == ALIVE and num_neighbors >= 4:
                    game.next_board[i][j] = DEAD
                    game.is_over = False
                # When a living cell has 1 or fewer neighbors => toggle to dead
                elif item == ALIVE and num_neighbors <= 1:
                    game.next_board[i][j] = DEAD
                    game.is_over = False
                else:
                    game.next_board[i][j] = item

        # Copy over the new board for next loop
        game.board = game.next_board.copy()
        time.sleep(0.3)

    # Print out score, sleep before we restore the terminal defaults
    print("Game over. Your score is {}.".format(counter))
    time.sleep(3)
    sys.exit(0)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        sys.exit(0)
