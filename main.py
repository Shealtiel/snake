import curses
import random
from operator import add, sub


class Coordinate(tuple):
    def __add__(self, other):
        res = list(map(add, self, other))
        return Coordinate(res)

    def __sub__(self, other):
        res = list(map(sub, self, other))
        return Coordinate(res)


class Snake:
    def __init__(self):
        self.body = [Coordinate((10, 5)), Coordinate((9, 5)), Coordinate((8, 5))]
        self.grow_points = 0

    @property
    def head(self):
        return self.body[0]

    def add_grow(self, points):
        self.grow_points += points

    def grow(self):
        if self.grow_points > 0:
            self.grow_points -= 1
        else:
            self.body = self.body[:-1]

    def move(self, new_direction):
        self.grow()

        if new_direction == 'up':
            self.body = [self.head - (0, 1), *self.body]
        if new_direction == 'down':
            self.body = [self.head + (0, 1), *self.body]
        if new_direction == 'left':
            self.body = [self.head - (1, 0), *self.body]
        if new_direction == 'right':
            self.body = [self.head + (1, 0), *self.body]


class Food:
    def __init__(self, coordinate, size=1):
        self.coordinate = coordinate
        self.size = size

    def __repr__(self):
        return f'{self.coordinate} - {self.size}'

    def __getitem__(self, item):
        return self.coordinate[item]


class Field:
    def __init__(self, max_x, max_y):
        self.max_x = max_x
        self.max_y = max_y
        self.cells = [Coordinate((x, y)) for x in range(max_x) for y in range(max_y)]
        self.snake = None
        self.food_set = set()
        self.turn = 0
        self.borders = {c for c in self.cells
                        if c[0] == 0
                        or c[1] == 0
                        or c[0] == self.max_x - 1
                        or c[1] == self.max_y - 1}

    def get_random_cells(self, k):
        return random.choices([c for c in self.cells if c not in self.borders], k=k)

    def add_snake(self):
        self.snake = Snake()
        return self.snake

    def add_food(self, k=2):
        random_food_set = {Food(coordinate, random.randint(1, 3)) for coordinate in self.get_random_cells(k)}
        self.food_set = {*self.food_set, *random_food_set}
        return self.food_set

    def add_to_borders(self, coordinates):
        self.borders = {*self.borders, *coordinates}
        return self.borders

    def check_food(self):
        for food in self.food_set:
            if food.coordinate == self.snake.head:
                self.snake.add_grow(food.size)
                self.food_set.remove(food)
                self.add_food(1)
                break

    def check_snake_alive(self):
        if self.snake.head in {*self.snake.body[1:], *self.borders}:
            return False
        return True


def draw_field(win, field: Field):
    win.border()

    for food in field.food_set:
        win.addstr(food.coordinate[1], food.coordinate[0], '123456'[food.size])

    for part in field.snake.body:
        win.addstr(part[1], part[0], '*')

    turn = str(field.turn)
    h, w = win.getmaxyx()
    win.addstr(0, w - len(turn), turn)


def main(stdscr):
    h, w = stdscr.getmaxyx()
    win = curses.newwin(h, w, 0, 0)

    curses.noecho()
    curses.cbreak()

    win.keypad(1)
    win.nodelay(0)

    curses.curs_set(0)

    # Create field
    field = Field(w, h)
    field.add_food()
    snake = field.add_snake()

    draw_field(win, field)

    win.refresh()

    c = win.getch()

    while True:
        curses.curs_set(0)

        win.nodelay(1)

        k = win.getch()
        c = k if k != -1 else c
        # win.addstr(0, 0, str(c))

        if c == ord('q'):
            break
        if c == curses.KEY_UP:
            snake.move('up')
        if c == curses.KEY_DOWN:
            snake.move('down')
        if c == curses.KEY_LEFT:
            snake.move('left')
        if c == curses.KEY_RIGHT:
            snake.move('right')

        if not field.check_snake_alive():
            break

        field.check_food()

        win.clear()
        draw_field(win, field)
        field.turn += 1

        win.refresh()
        curses.napms(100)

    win.addstr(0, 1, f'YOU DIED. SCORE {len(snake.body)}')
    win.refresh()

    win.nodelay(0)
    win.getch()

    win.keypad(0)
    curses.endwin()


curses.wrapper(main)
