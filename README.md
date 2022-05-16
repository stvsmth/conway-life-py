# Conway’s Game of Life — Python / curses

A Python implementation of [Conway’s Game of Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

This is a fairly naive implementation with hard game borders. That is a glider that reaches the edge of
the game board will die rather than wrap around to the other side.

This was the first thing I wrote while attending the [Recurse Center](https://recurse.com). Thanks to [5cotts](https://github.com/5cotts/)
who paired with me on this for a great start to an amazing 12-week experience.

## Installation

This program uses Python 3.8 or higher (we use the walrus operator) and requires nothing but the standard library.

As this program uses `curses`, it will not work on Windows without some additional effort. Perhaps I will write a
Rust version.

## Example

![Demo screen cast](https://f004.backblazeb2.com/file/stvsmth-random-files/conway-life-demo.gif)
