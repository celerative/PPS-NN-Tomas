import pygame as pg
import numpy as np

pg.init()
screen = pg.display.set_mode((500, 500))
done = False
game_refresh = True
ui_refresh = True

'''
Board possible positions (x,y):
x --> 0 - 3 - 6 - 9 - 12
y --> 0 - 4 - 8 - 12 - 16 - 20

Board schem:
    x0  x3  x6  x9  x12
    ---------------------
y0  |   |   |   |   |   |
    ---------------------
y4  |   |   |   |   |   |
    ---------------------
y8  |   |   |   |   |   |
    ---------------------
y12 |   |   |   |   |   |
    ---------------------
y16 |   |   |   |   |   |
    ---------------------
y20 |   |   |   |   |   |
    ---------------------
'''

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
opponents = []
player = None

# game colors
game_color_bg = (255, 255, 255)  # "#FFFFFF"
game_color_line = (221, 221, 221)  # "#DDDDDD"
game_color_wall = (85, 85, 85)  # "#555555"
game_color_opponent = (0, 0, 0)  # "#000000"
game_color_player = (92, 150, 24)  # "#5c9618"
game_color_player_ = (48, 74, 18)  # "#304a12"

# game states
game_state_multi_steps = False
game_state_score = 0

# ui vars

# timing
clock = pg.time.Clock()
FPS = 10


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.last_x = -1
        self.next_x = -1


def draw_grid():
    for i in range(game_cols + 1):
        pg.draw.line(screen, game_color_line, (block_size * i, 0), (block_size * i, game_H), grid_line_W)

    for i in range(game_rows + 1):
        pg.draw.line(screen, game_color_line, (0, block_size * i), (game_W, block_size * i), grid_line_W)


def draw_rect(x, y, rect_color):
    if y < game_rows:
        pg.draw.rect(screen, rect_color, pg.Rect(x * block_size + grid_line_W, y * block_size + grid_line_W, block_size - grid_line_W, block_size - grid_line_W))
        pg.draw.rect(screen, (255, 255, 255), pg.Rect(x * block_size + grid_line_W + 1, y * block_size + grid_line_W + 1, block_size - grid_line_W - 2, block_size - grid_line_W - 2))
        pg.draw.rect(screen, rect_color, pg.Rect(x * block_size + 2 * grid_line_W, y * block_size + 2 * grid_line_W, block_size - 3 * grid_line_W, block_size - 3 * grid_line_W))


def draw_car(x, y, car_color):
    x += car_width  # left wall offset
    draw_rect(x + 1, y, car_color)
    draw_rect(x + 1, y + 1, car_color)
    draw_rect(x + 1, y + 2, car_color)
    draw_rect(x, y + 1, car_color)
    draw_rect(x + 2, y + 1, car_color)
    draw_rect(x, y + 3, car_color)
    draw_rect(x + 2, y + 3, car_color)


def draw_walls():
    global walls_state
    state = walls_state
    for i in range(game_rows):
        if state < 2:
            draw_rect(1, i, game_color_wall)
            draw_rect(game_cols - 2, i, game_color_wall)
        state = (state + 1) % 3


def move_player():
    global player
    player.next_x = player.x
    # keyboard control
    if True:
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            if player.x > 0:
                player.next_x = player.x - car_width
        elif pressed[pg.K_RIGHT]:
            if player.x < 12:
                player.next_x = player.x + car_width
    # trained NET control
    elif True:
        pass
    # evolutive control
    elif True:
        pass
    player.last_x = player.x
    if game_state_multi_steps:
        while player.next_x != player.x:
            if player.next_x < player.x:
                player.x -= car_width
                draw_car(player.x, player.x, game_color_player_)
            else:
                player.x += car_width
                draw_car(player.x, player.x, game_color_player_)
            # TODO is_crashed = check_crash()
    else:
        player.x = player.next_x


def check_crash():
    crash_car_id = None
    global opponents
    global player
    for op in opponents:
        if op.y > (player.y - car_height) and op.y < (player.y + car_height - 1):
            pass


def shuffle_needed():
    pass


def move_opponents():
    global opponents
    for op in opponents:
        if op.y < game_rows:
            op.y += 1
        else:
            global game_state_score
            game_state_score += 1
            op.x = np.random.randint(5) * car_width
            op.y -= car_height * 8 - 1
    while shuffle_needed():
        pass


def init_game():
    pg.draw.rect(screen, game_color_bg, pg.Rect(0, 0, game_W, game_H))
    draw_grid()
    draw_walls()
    # player
    global player
    player = Player(2 * car_width, 5 * car_height)
    draw_car(player.x, player.y, game_color_player)
    # opponents
    global opponents
    opponents = []
    for i in range(opponents_number):
        # opponents.append(Position(np.random.randint(5) * car_width, -car_height * np.random.randint(1, i + 2)))
        opponents.append(Position(np.random.randint(5) * car_width, -car_height * i))
    # TODO set game_state_vars
    global game_state_score
    game_state_score = 0


def update_game():
    # walls
    global walls_state
    walls_state = (walls_state + 1) % 3
    # player
    move_player()
    # opponents
    move_opponents()


def draw_game():
    pg.draw.rect(screen, game_color_bg, pg.Rect(0, 0, game_W, game_H))
    draw_grid()
    draw_walls()
    # player
    global player
    draw_car(player.x, player.y, game_color_player)
    # opponents
    global opponents
    for op in opponents:
        if op.x >= 0:
            draw_car(op.x, op.y, game_color_opponent)


def init_ui():
    pass


def update_ui():
    pass


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
    if game_refresh:
        update_game()
    if ui_refresh:
        update_ui()
    draw_game()
    draw_ui()
    pg.display.flip()
    clock.tick(FPS)
