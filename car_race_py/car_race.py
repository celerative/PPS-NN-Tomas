import pygame as pg
import numpy as np
import Buttons
import NET_model
import ES

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

Mode 0: Manual game
Mode 1: Run Trained NET
Mode 2: Train NET with Reinforce Learning
Mode 3: Train NET with Evolutive Population

'''

# data
grid = None

# NET
model = None
model_path_1 = "NET_model_1.h5"
model_path_2 = "NET_model_2.h5"
model_pred_enable = False

# ES
ES_population_size = 10
ES_indiv = None
ES_is_running = False
ES_seed = []
ES_best_score = 0

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
game_state_crashed = False
game_state_running = False

# ui vars
playButton = None
speedUpButton = None
speedDownButton = None
modeUpButton = None
modeDownButton = None

# ui states
ui_state_playButton = "Play"
ui_state_speed = 10
ui_state_mode = 0
ui_state_mode_string = ["Manual", "UseNET", "TrainRL", "TrainES"]

# timing
clock = pg.time.Clock()
FPS = 60
FPS_default = 60
freq_count = 0


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


def init_NET_model():
    global model
    model = NET_model.NET_model()
    model.load_model(model_path_1)


def init_ES():
    global ES_population_size
    global ES_seed
    model = NET_model.NET_model()
    model.load_model("./ES_models_0/ES_gen03_fit355.h5")
    ES_seed.append(ES.ES_indiv(model, 0))

    model = NET_model.NET_model()
    model.load_model("./ES_models_0/ES_gen08_fit367.h5")
    ES_seed.append(ES.ES_indiv(model, 1))

    model = NET_model.NET_model()
    model.load_model("./ES_models_1/ES_gen02_fit566.h5")
    ES_seed.append(ES.ES_indiv(model, 2))

    model = NET_model.NET_model()
    model.load_model("./ES_models_1/ES_gen04_fit340.h5")
    ES_seed.append(ES.ES_indiv(model, 3))

    model = NET_model.NET_model()
    model.load_model("./ES_models_1/ES_gen10_fit588.h5")
    ES_seed.append(ES.ES_indiv(model, 4))

    model = NET_model.NET_model()
    model.load_model("./ES_models_1/ES_gen11_fit323.h5")
    ES_seed.append(ES.ES_indiv(model, 5))

    ES.new_population(ES_population_size, ES_seed, True)
    global ES_best_score
    ES_best_score = 0
    global ES_indiv
    ES_indiv = ES.get_next_indiv()


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
    global game_state_multi_steps
    global ui_state_mode
    global grid
    grid[0][player.y // car_height * 5 + player.x // car_width] = .5
    # print(grid)
    # print("[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "[{} | {} | {} | {} | {} ]\n"
    #       "------------------------------"
    #       .format(*grid[0]))
    # Mode 0: Manual game
    if ui_state_mode == 0:
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            if player.x > 0:
                player.next_x = player.x - car_width
        elif pressed[pg.K_RIGHT]:
            if player.x < 12:
                player.next_x = player.x + car_width
        game_state_multi_steps = False
    # Mode 1: Run Trained NET
    elif ui_state_mode == 1:
        if model_pred_enable:
            global model
            pred = model.predict(grid)
            # print(pred)
            # print(np.argmax(pred[0]))
            player.next_x = np.argmax(pred[0]) * car_width
            global model_pred_enable
            # model_pred_enable = False  # should work always because positions were normalized
            game_state_multi_steps = True
    # Mode 2: Train NET with Reinforce Learning
    elif ui_state_mode == 2:
        pass
    # Mode 3: Train NET with Evolutive Population
    elif ui_state_mode == 3:
        if model_pred_enable:
            global ES_indiv
            pred = ES_indiv.model.predict(grid)
            # print(pred)
            # print(np.argmax(pred[0]))
            player.next_x = np.argmax(pred[0]) * car_width
            global model_pred_enable
            # model_pred_enable = False  # should work always because positions were normalized
            game_state_multi_steps = True
    grid[0][player.y // car_height * 5 + player.x // car_width] = 0
    player.last_x = player.x
    global game_state_crashed
    game_state_crashed = check_crash()
    if not game_state_crashed:
        if game_state_multi_steps:
            while player.next_x != player.x:
                if player.next_x < player.x:
                    player.x -= car_width
                    print("<--")
                else:
                    player.x += car_width
                    print("-->")
                game_state_crashed = check_crash()
                if game_state_crashed:
                    break
        else:
            if player.next_x < player.x:
                print("<--")
            elif player.next_x > player.x:
                print("-->")
            player.x = player.next_x
            game_state_crashed = check_crash()
    if game_state_crashed:
        print("Game Over")
    grid[0][player.y // car_height * 5 + player.x // car_width] = .5
    print("#-----------------------------------------------------------------#")


def check_crash():
    global opponents
    global player
    for op in opponents:
        if np.absolute(op.x - player.x) < car_width and np.absolute(op.y - player.y) < car_height:
            return True
    return False


def shuffle_needed():
    global opponents
    for i in range(len(opponents) - 1):
        for j in range(i + 1, len(opponents)):
            if opponents[j].x == opponents[i].x and np.absolute(opponents[j].y - opponents[i].y) < 2 * car_height:
                return True
            if opponents[j].y == opponents[i].y and np.absolute(opponents[j].x - opponents[i].x) <= car_width:
                return True
    ###
    # check for holes in creasent diagonals (right and left diags) for each opponent
    return False


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

    deadlock = 0
    while shuffle_needed():
        if deadlock > 10:
            print("Deadlock unsolve")
            global game_state_crashed
            game_state_crashed = True
            break
        deadlock += 1
        for i in range(len(opponents) - 1):
            for j in range(i + 1, len(opponents)):
                while opponents[j].y == opponents[i].y and np.absolute(opponents[j].x - opponents[i].x) <= car_width:
                    if np.random.random() > 0.5:
                        opponents[j].x = np.random.randint(5) * car_width
                    else:
                        opponents[j].y -= car_height
                while opponents[j].x == opponents[i].x and np.absolute(opponents[j].y - opponents[i].y) < 2 * car_height:
                    opponents[j].y -= car_height
        ###
        # delete diagonal of opponents
    global grid
    for op in opponents:
        if op.y >= 0 and op.y < game_rows:
            if op.y % car_height:
                global model_pred_enable
                model_pred_enable = True
            grid[0][op.y // car_height * 5 + op.x // car_width] = 1


def init_game():
    pg.draw.rect(screen, game_color_bg, pg.Rect(0, 0, game_W, game_H))
    draw_grid()
    draw_walls()
    global game_state_score
    # set mode
    global ui_state_mode
    # Mode 1: Run Trained NET
    if ui_state_mode == 1:
        init_NET_model()
    # Mode 2: Train NET with Reinforce Learning
    elif ui_state_mode == 2:
        pass
    # Mode 3: Train NET with Evolutive Population
    elif ui_state_mode == 3:
        global ES_is_running
        if ES_is_running:
            global ES_indiv
            global ES_best_score
            if game_state_score > ES_best_score:
                ES_best_score = game_state_score
            ES_indiv.fitness = game_state_score
            ES_indiv = ES.get_next_indiv()
        else:
            ES_is_running = True
            init_ES()
    # data
    global grid
    grid = np.zeros(shape=(1, 30), dtype=float)
    # player
    global player
    player = Player(2 * car_width, 5 * car_height)
    draw_car(player.x, player.y, game_color_player)
    grid[0][player.y // car_height * 5 + player.x // car_width] = .5
    # opponents
    global opponents
    opponents = []
    # # if opponents are located completely random, could cause deadlock
    # # for i in range(opponents_number):
    # #     opponents.append(Position(np.random.randint(4) * car_width, -car_height * np.random.randint(1, i + 2)))
    # to solve initial deadlock, positions are not fully random
    opponents.append(Position(0 * car_width, -car_height * np.random.randint(1, 3)))
    opponents.append(Position(0 * car_width, -car_height * np.random.randint(3, 5)))
    opponents.append(Position(2 * car_width, -car_height * np.random.randint(1, 3)))
    opponents.append(Position(2 * car_width, -car_height * np.random.randint(3, 5)))
    opponents.append(Position(4 * car_width, -car_height * np.random.randint(1, 3)))
    opponents.append(Position(4 * car_width, -car_height * np.random.randint(3, 5)))
    # game_state_vars
    game_state_score = 0
    global game_state_crashed
    game_state_crashed = False
    global freq_count
    freq_count = 0


def update_game():
    global game_state_crashed
    global game_state_running
    if game_state_crashed:
        global ui_state_mode
        if ui_state_mode == 3:
            init_game()
        else:
            game_state_running = False
    else:
        if game_state_running:
            # walls
            global walls_state
            walls_state = (walls_state + 1) % 3
            # opponents
            move_opponents()
            # player
            move_player()
            # reset data
            global grid
            grid = np.zeros(shape=(1, 30), dtype=float)


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


def write_text(surface, text, text_color, length, height, x, y):
    font_size = 2 * int(length // len(text))
    myFont = pg.font.SysFont("Calibri", font_size)
    myText = myFont.render(text, 1, text_color)
    surface.blit(myText, ((x + length / 2) - myText.get_width() / 2, (y + height / 2) - myText.get_height() / 2))
    return surface


def init_ui():
    pg.display.set_caption("Car Race")
    global playButton
    playButton = Buttons.Button()
    global speedUpButton
    speedUpButton = Buttons.Button()
    global speedDownButton
    speedDownButton = Buttons.Button()
    global modeUpButton
    modeUpButton = Buttons.Button()
    global modeDownButton
    modeDownButton = Buttons.Button()
    # create buttons
    playButton.create_button(screen, (107, 142, 35), game_W + 10, 30, 145, 50, 0, ui_state_playButton, (255, 255, 255))
    speedDownButton.create_button(screen, (107, 142, 35), game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
    speedUpButton.create_button(screen, (107, 142, 35), game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
    modeDownButton.create_button(screen, (107, 142, 35), game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
    modeUpButton.create_button(screen, (107, 142, 35), game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))


def update_ui():
    global game_state_running
    global ui_state_playButton
    if not game_state_running:
        ui_state_playButton = "Play"
    else:
        ui_state_playButton = "Stop"
    global FPS
    global ui_state_speed
    FPS = ui_state_speed


def draw_ui():
    # play button
    global playButton
    global ui_state_playButton
    playButton.create_button(screen, (107, 142, 35), game_W + 10, 30, 145, 50, 0, ui_state_playButton, (255, 255, 255))
    # score
    global game_state_score
    write_text(screen, "Score: " + str(game_state_score), (107, 142, 35), 145, 40, game_W + 10, 100)
    # speed
    global ui_state_speed
    write_text(screen, "Speed: " + str(ui_state_speed), (107, 142, 35), 145, 40, game_W + 10, 140)
    global speedDownButton
    if ui_state_speed > 1:
        speedDownButton.create_button(screen, (107, 142, 35), game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
    global speedUpButton
    speedUpButton.create_button(screen, (107, 142, 35), game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
    # mode
    global ui_state_mode
    write_text(screen, "Mode: ", (107, 142, 35), 120, 30, game_W + 20, 240)
    global ui_state_mode_string
    write_text(screen, ui_state_mode_string[ui_state_mode], (107, 142, 35), 80, 10, game_W + 50, 275)
    if not game_state_running:
        if ui_state_mode > 0:
            global modeDownButton
            modeDownButton.create_button(screen, (107, 142, 35), game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
        if ui_state_mode < 3:
            global modeUpButton
            modeUpButton.create_button(screen, (107, 142, 35), game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))
    # ES info
    global game_state_running
    if ui_state_mode == 3 and game_state_running:
        global ES_indiv
        global ES_best_score
        write_text(screen, "Gen: " + str(ES_indiv.generation), (107, 142, 35), 60, 20, 20, game_H + 10)
        write_text(screen, "ID: " + str(ES_indiv.indiv_id), (107, 142, 35), 40, 20, 20, game_H + 30)
        write_text(screen, "Best score:" + str(ES_best_score), (107, 142, 35), 150, 20, 20, game_H + 50)


init_game()
init_ui()

while not done:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if playButton.pressed(pg.mouse.get_pos()):
                if game_state_running:
                    game_state_running = False
                else:
                    init_game()
                    game_state_running = True
            if speedUpButton.pressed(pg.mouse.get_pos()):
                ui_state_speed += 1
            if speedDownButton.pressed(pg.mouse.get_pos()):
                if ui_state_speed > 1:
                    ui_state_speed -= 1
            if not game_state_running:
                if modeUpButton.pressed(pg.mouse.get_pos()):
                    if ui_state_mode < 3:
                        ui_state_mode += 1
                if modeDownButton.pressed(pg.mouse.get_pos()):
                    if ui_state_mode > 0:
                        ui_state_mode -= 1
    # stablish frequecies relation (FPS and speed)
    if ui_state_speed < FPS:
        FPS = FPS_default
        freq_count += 1
        if ui_state_speed == freq_count % ui_state_speed:
            game_refresh = True
        if freq_count >= FPS_default:
            if ui_state_speed / FPS > .5:
                game_refresh = True
            freq_count = 0
    else:
        FPS = ui_state_speed
        game_refresh = True
    if game_refresh:
        update_game()
        game_refresh = False
    if ui_refresh:
        update_ui()
    draw_game()
    draw_ui()
    pg.display.flip()
    clock.tick(FPS)
