from __future__ import annotations

import curses
from dataclasses import dataclass
from enum import Enum
from random import Random
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Tuple

random = Random(x=1389075)


@dataclass(frozen=True)
class Cell:
    x: int
    y: int

    def move(self, direction: Direction) -> Cell:
        return Cell(self.x + direction.value.x, self.y + direction.value.y)

    @classmethod
    def get_random(cls, max_x: int, max_y: int) -> Cell:
        return cls(random.randint(0, max_x), random.randint(0, max_y))


class Direction(Enum):
    value: Cell
    UP = Cell(0, -1)
    DOWN = Cell(0, 1)
    LEFT = Cell(-1, 0)
    RIGHT = Cell(1, 0)

    def is_opposite(self, to: Direction) -> bool:
        return self.value.x + to.value.x == 0 and self.value.y + to.value.y == 0


@dataclass(frozen=True)
class Snake:
    cells: List[Cell]
    direction: Direction
    eaten_apples: int = 0

    @property
    def head(self) -> Cell:
        return self.cells[0]

    @property
    def tail(self) -> List[Cell]:
        return self.cells[1:]

    def move(self) -> Snake:
        new_head = self.head.move(self.direction)
        new_tail = self.cells[:-1] if not self.eaten_apples else self.cells
        return Snake(
            cells=[new_head, *new_tail],
            direction=self.direction,
            eaten_apples=max(0, self.eaten_apples - 1)
        )

    def turn(self, direction: Optional[Direction]) -> Snake:
        if not direction or direction.is_opposite(self.direction):
            return self
        return Snake(cells=self.cells, direction=direction)

    def eat(self, apples: Apples) -> Tuple[Snake, Apples]:
        if self.head not in apples.cells:
            return self, apples
        return (
            Snake(
                cells=self.cells,
                direction=self.direction,
                eaten_apples=self.eaten_apples + 1
            ),
            Apples(
                width=apples.width,
                height=apples.height,
                cells=apples.cells - {self.head}
            ).grow(self)
        )


@dataclass(frozen=True)
class Apples:
    width: int
    height: int
    cells: FrozenSet[Cell] = frozenset()

    def grow(self, snake: Snake) -> Apples:
        new_cell = Cell.get_random(self.width - 1, self.height - 1)
        while new_cell in snake.cells:
            new_cell = Cell.get_random(self.width - 1, self.height - 1)
        return Apples(
            width=self.width,
            height=self.height,
            cells=self.cells | {new_cell}
        )


@dataclass(frozen=True)
class Game:
    width: int
    height: int
    snake: Snake
    apples: Apples

    @property
    def is_over(self) -> bool:
        return (
            self.snake.head in self.snake.tail or
            not all(0 <= c.x < self.width and 0 <= c.y < self.height for c in self.snake.cells)
        )

    @property
    def score(self) -> int:
        return len(self.snake.cells)

    def update(self, direction: Optional[Direction]) -> Game:
        if self.is_over:
            return self
        new_snake, new_apples = self.snake.turn(direction).move().eat(self.apples)
        return Game(
            width=self.width,
            height=self.height,
            snake=new_snake,
            apples=new_apples
        )


def draw(window, game: Game) -> None:
    window.clear()
    window.box()

    for c in game.apples.cells:
        window.addstr(c.y + 1, c.x + 1, '*')
    for c in game.snake.tail:
        window.addstr(c.y + 1, c.x + 1, 'o')
    window.addstr(game.snake.head.y + 1, game.snake.head.x + 1, 'Q')

    if game.is_over:
        window.addstr(0, 1, 'The game is over')
        window.addstr(1, 1, f'Score is {game.score}')

    window.refresh()


def main(window=curses.initscr()):
    curses.curs_set(0)
    curses.halfdelay(2)

    direction = {
        'w': Direction.UP,
        'a': Direction.LEFT,
        's': Direction.DOWN,
        'd': Direction.RIGHT
    }
    height = 10
    width = 20
    window.resize(height + 2, width + 2)
    game = Game(
        width=width,
        height=height,
        snake=Snake(
            cells=[Cell(3, 1), Cell(2, 1), Cell(1, 1)],
            direction=Direction.RIGHT
        ),
        apples=Apples(
            width=width,
            height=height,
            cells=frozenset([Cell.get_random(width - 1, height - 1)])
        )
    )
    input_ch = 0
    pause = False
    while chr(input_ch) != 'q':
        draw(window, game)
        input_ch = max(window.getch(), 0)
        if chr(input_ch) == 'p':
            pause = not pause
        if not pause:
            game = game.update(direction.get(chr(input_ch)))


if __name__ == '__main__':
    curses.wrapper(main)
