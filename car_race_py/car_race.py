import pygame as pg
import numpy as np

pg.init()
screen = pg.display.set_mode((500, 500))
done = False

# game vars
game_cols = 21
game_rows = 24
game_H = 384
block_size = game_H / game_rows  # block size 16
game_W = game_cols * block_size
grid_line_W = 2
car_width = 3
car_height = 4
walls_state = 0  # 0, 1 or 2
opponents_number = 6

# game colors
game_color_bg = (255, 255, 255)  # "#FFFFFF"
game_color_line = (221, 221, 221)  # "#DDDDDD"
game_color_wall = (85, 85, 85)  # "#555555"

# timing
clock = pg.time.Clock()
FPS = 60


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


def draw_grid():
    for i in range(game_cols + 1):
        pg.draw.line(screen, game_color_line, (block_size * i, 0), (block_size * i, game_H), grid_line_W)

    for i in range(game_rows + 1):
        pg.draw.line(screen, game_color_line, (0, block_size * i), (game_W, block_size * i), grid_line_W)


def draw_rect(x, y, rect_color):
    pg.draw.rect(screen, rect_color, pg.Rect(x * block_size + grid_line_W, y * block_size + grid_line_W, block_size - grid_line_W, block_size - grid_line_W))
    pg.draw.rect(screen, (255, 255, 255), pg.Rect(x * block_size + grid_line_W + 1, y * block_size + grid_line_W + 1, block_size - grid_line_W - 2, block_size - grid_line_W - 2))
    pg.draw.rect(screen, rect_color, pg.Rect(x * block_size + 2 * grid_line_W, y * block_size + 2 * grid_line_W, block_size - 3 * grid_line_W, block_size - 3 * grid_line_W))


def draw_car(x, y, car_color):
    draw_rect(x + 1, y, car_color)
    draw_rect(x + 1, y + 1, car_color)
    draw_rect(x + 1, y + 2, car_color)
    draw_rect(x, y + 1, car_color)
    draw_rect(x + 2, y + 1, car_color)
    draw_rect(x, y + 3, car_color)
    draw_rect(x + 2, y + 3, car_color)


def draw_walls(move):
    global walls_state
    if (move):
        walls_state = (walls_state + 1) % 3
    state = walls_state
    for i in range(game_rows):
        if state < 2:
            draw_rect(1, i, game_color_wall)
            draw_rect(game_cols - 2, i, game_color_wall)
        state = (state + 1) % 3


def init_game():
    pg.draw.rect(screen, game_color_bg, pg.Rect(0, 0, game_W, game_H))
    draw_grid()
    draw_walls(False)
    # draw_car()


def init_ui():
    pass


def draw_game():
    pg.draw.rect(screen, game_color_bg, pg.Rect(0, 0, game_W, game_H))
    draw_grid()
    draw_walls(True)
    # opponents
    global opponents
    opponents = []
    for i in range(3):
        opponents.append(Position(np.random.randint(5) * car_width, -8))
        opponents.append(Position(np.random.randint(5) * car_width, -24))


# 0 - 3 - 6 - 9 - 12
# 0 - 4 - 8 - 12 - 16 - 20


def draw_ui():
    pass


init_game()
init_ui()

while not done:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            done = True

    draw_game()
    draw_ui()
    pg.display.flip()
    clock.tick(FPS)
