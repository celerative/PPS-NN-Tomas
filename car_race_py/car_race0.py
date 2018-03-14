from sys import argv
import pygame as pg
import numpy as np
from car_race_RLreward import get_reward
import Buttons
import NET_model
import ES
import RL

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

# NET
if len(argv) < 2:  # load path from args
    model_path = "./pre_train_models/NET_model.h5"
else:
    model_path = argv[1]
print("Using model: '" + model_path + "'")
model = None
model_pred_enable = False

# ES
ES_population_size = 10
ES_population = None
ES_ind = None
ES_is_running = False
ES_seed = []
ES_best_score = 0

# RL
RL_ind = None
RL_best_score = 0
RL_games_played = 0

# timing
clock = pg.time.Clock()


class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self._last_x = -1
        self._next_x = -1
        self.score = 0

    def move(self, opponents, mode, Model):
        board = np.zeros((1, 30))
        move_enable = False
        for op in opponents:
            if op.y >= 0 and op.y < CarRaceGame.game_rows:
                if op.y % CarRaceGame.car_height == 0:
                    move_enable = True
                board[0][op.y // CarRaceGame.car_height * 5 + op.x // CarRaceGame.car_width] = 1
        self._next_x = self.x
        board[0][self.y // CarRaceGame.car_height * 5 + self.x // CarRaceGame.car_width] = .5
        if mode == 0:
            # Mode 0: Manual game
            self._manual()
            multi_steps = False
        elif mode == 2:
            # Mode 2: Train NET with Reinforce Learning
            # if np.random.random() > 0.95:  # percentage to take random action
            if False:  # force to predict action
                if move_enable:
                    self._next_x = np.random.randint(5) * CarRaceGame.car_width
                    print("RANDOM")
            else:
                self._network(board, Model)
            multi_steps = True
        else:
            # Mode 1: Run Trained NET
            # Mode 3: Train NET with Evolutive Population
            self._network(board, Model)
            multi_steps = True
        #####################
        self._last_x = self.x
        crashed = self.check_crash(opponents)
        if not crashed:
            if multi_steps:
                while self._next_x != self.x:
                    if self._next_x < self.x:
                        self.x -= CarRaceGame.car_width
                        print("<--")
                    else:
                        self.x += CarRaceGame.car_width
                        print("-->")
                    crashed = self.check_crash(opponents)
                    if crashed:
                        break
            else:
                if self._next_x < self.x:
                    print("<--")
                elif self._next_x > self.x:
                    print("-->")
                self.x = self._next_x
                crashed = self.check_crash(opponents)
        # if crash, return False
        return crashed

    def check_crash(self, opponents):
        for op in opponents:
            if np.absolute(op.x - self.x) < CarRaceGame.car_width and np.absolute(op.y - self.y) < CarRaceGame.car_height:
                return True
        return False

    def _manual(self):
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            if self.x > 0:
                self._next_x = self.x - CarRaceGame.car_width
        elif pressed[pg.K_RIGHT]:
            if self.x < 12:
                self._next_x = self.x + CarRaceGame.car_width

    def _network(self, board, Model):
        pred = Model.predict(board)
        self._next_x = np.argmax(pred[0]) * CarRaceGame.car_width


class CarRaceGame:

    game_cols = 21
    game_rows = 24
    game_H = 384
    block_size = game_H / game_rows  # block size 16
    game_W = game_cols * block_size
    car_width = 3
    car_height = 4

    def __init__(self):
        # game vars
        self._grid_line_W = 2
        self._walls_state = 0  # 0, 1 or 2
        self._opponents_number = 6
        self.opponents = []
        self.player = None

        # game colors
        self._game_color_bg = (255, 255, 255)  # "#FFFFFF"
        self._game_color_line = (221, 221, 221)  # "#DDDDDD"
        self._game_color_wall = (85, 85, 85)  # "#555555"
        self._game_color_opponent = (0, 0, 0)  # "#000000"
        self._game_color_player = (92, 150, 24)  # "#5c9618"
        self._game_color_player_ = (48, 74, 18)  # "#304a12"

        # game states
        self.game_state_multi_steps = False
        self.game_state_score = 0
        self.game_state_crashed = False
        self.game_state_running = False

        # init game
        self.init_game()

    def draw_grid(self):
        for i in range(CarRaceGame.game_cols + 1):
            pg.draw.line(screen, self._game_color_line, (CarRaceGame.block_size * i, 0), (CarRaceGame.block_size * i, CarRaceGame.game_H), self._grid_line_W)

        for i in range(CarRaceGame.game_rows + 1):
            pg.draw.line(screen, self._game_color_line, (0, CarRaceGame.block_size * i), (CarRaceGame.game_W, CarRaceGame.block_size * i), self._grid_line_W)

    def draw_rect(self, x, y, rect_color):
        if y < CarRaceGame.game_rows:
            pg.draw.rect(screen, rect_color, pg.Rect(x * CarRaceGame.block_size + self._grid_line_W, y * CarRaceGame.block_size + self._grid_line_W, CarRaceGame.block_size - self._grid_line_W, CarRaceGame.block_size - self._grid_line_W))
            pg.draw.rect(screen, (255, 255, 255), pg.Rect(x * CarRaceGame.block_size + self._grid_line_W + 1, y * CarRaceGame.block_size + self._grid_line_W + 1, CarRaceGame.block_size - self._grid_line_W - 2, CarRaceGame.block_size - self._grid_line_W - 2))
            pg.draw.rect(screen, rect_color, pg.Rect(x * CarRaceGame.block_size + 2 * self._grid_line_W, y * CarRaceGame.block_size + 2 * self._grid_line_W, CarRaceGame.block_size - 3 * self._grid_line_W, CarRaceGame.block_size - 3 * self._grid_line_W))

    def draw_car(self, x, y, car_color):
        x += CarRaceGame.car_width  # left wall offset
        self.draw_rect(x + 1, y, car_color)
        self.draw_rect(x + 1, y + 1, car_color)
        self.draw_rect(x + 1, y + 2, car_color)
        self.draw_rect(x, y + 1, car_color)
        self.draw_rect(x + 2, y + 1, car_color)
        self.draw_rect(x, y + 3, car_color)
        self.draw_rect(x + 2, y + 3, car_color)

    def draw_walls(self):
        state = self._walls_state
        for i in range(CarRaceGame.game_rows):
            if state < 2:
                self.draw_rect(1, i, self._game_color_wall)
                self.draw_rect(CarRaceGame.game_cols - 2, i, self._game_color_wall)
            state = (state + 1) % 3

    def shuffle_needed(self):
        for i in range(len(self.opponents) - 1):
            for j in range(i + 1, len(self.opponents)):
                if self.opponents[j].x == self.opponents[i].x and np.absolute(self.opponents[j].y - self.opponents[i].y) < 2 * CarRaceGame.car_height:
                    return True
                if self.opponents[j].y == self.opponents[i].y and np.absolute(self.opponents[j].x - self.opponents[i].x) <= CarRaceGame.car_width:
                    return True
        ###
        # check for holes in creasent diagonals (right and left diags) for each opponent
        aux_grid = np.zeros(shape=(1, 30), dtype=float)
        for op in self.opponents:
            if op.y < 0 and op.y > -CarRaceGame.game_rows:
                aux_grid[0][(op.y + CarRaceGame.game_rows) // CarRaceGame.car_height * 5 + op.x // CarRaceGame.car_width] = 1
        while get_reward(aux_grid) == -1:
            ###
            # delete diagonal self.opponents
            index = np.random.randint(0, len(self.opponents))
            if self.opponents[index].y < 0:
                self.opponents[index].y -= CarRaceGame.car_height * 2
            aux_grid = np.zeros(shape=(1, 30), dtype=float)
            for op in self.opponents:
                if op.y < 0 and op.y > -CarRaceGame.game_rows:
                    aux_grid[0][(op.y + CarRaceGame.game_rows) // CarRaceGame.car_height * 5 + op.x // CarRaceGame.car_width] = 1
        return False

    def move_opponents(self):
        for op in self.opponents:
            if op.y < CarRaceGame.game_rows:
                op.y += 1
            else:
                self.game_state_score += 1
                op.x = np.random.randint(5) * CarRaceGame.car_width
                op.y -= CarRaceGame.car_height * 8 - 1

        deadlock = 0
        while self.shuffle_needed():
            if deadlock > 10:
                print("Deadlock unsolve")
                self.game_state_crashed = True
                break
            deadlock += 1
            for i in range(len(self.opponents) - 1):
                for j in range(i + 1, len(self.opponents)):
                    while self.opponents[j].y == self.opponents[i].y and np.absolute(self.opponents[j].x - self.opponents[i].x) <= CarRaceGame.car_width:
                        if np.random.random() > 0.5:
                            self.opponents[j].x = np.random.randint(5) * CarRaceGame.car_width
                        else:
                            self.opponents[j].y -= CarRaceGame.car_height
                    while self.opponents[j].x == self.opponents[i].x and np.absolute(self.opponents[j].y - self.opponents[i].y) < 2 * CarRaceGame.car_height:
                        self.opponents[j].y -= CarRaceGame.car_height

    def init_game(self):
        pg.draw.rect(screen, self.game_color_bg, pg.Rect(0, 0, CarRaceGame.game_W, CarRaceGame.game_H))
        self.draw_grid()
        self.draw_walls()
        # set mode
        # Mode 1: Run Trained NET
        if ui_state_mode == 1:
            init_NET(model_path)
        # Mode 2: Train NET with Reinforce Learning
        elif ui_state_mode == 2:
            RL_best_score
            if game_state_score > RL_best_score:
                RL_best_score = self.game_state_score
            init_RL()
        # Mode 3: Train NET with Evolutive Population
        elif ui_state_mode == 3:
            ES_is_running
            if ES_is_running:
                if self._game_state_score > ES_best_score:
                    ES_best_score = self.game_state_score
                ES_ind.fitness = self.game_state_score
                ES_population
                ES_ind = ES_population.get_next_indiv()
            else:
                ES_is_running = True
                init_ES()
        # player
        player = Player(2 * CarRaceGame.car_width, 5 * CarRaceGame.car_height)
        self.draw_car(player.x, player.y, self._game_color_player)
        # opponents
        opponents = []
        # if opponents are located completely random, could cause deadlock
        # for i in range(opponents_number):
        #     opponents.append(Position(np.random.randint(4) * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(1, i + 2)))
        # to solve initial deadlock, positions are not fully random
        opponents.append(Position(0 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(1, 3)))
        opponents.append(Position(0 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(3, 5)))
        opponents.append(Position(2 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(1, 3)))
        opponents.append(Position(2 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(3, 5)))
        opponents.append(Position(4 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(1, 3)))
        opponents.append(Position(4 * CarRaceGame.car_width, -CarRaceGame.car_height * np.random.randint(3, 5)))
        # game_state_vars
        self.game_state_score = 0
        self.game_state_crashed
        self.game_state_crashed = False

    def update_game(self):
        if self.game_state_crashed:
            if ui_state_mode == 2:
                self.init_game()
                RL_games_played += 1
            elif ui_state_mode == 3:
                self.init_game()
            else:
                game_state_running = False
        else:
            if game_state_running:
                # walls
                self._walls_state
                self._walls_state = (self._walls_state + 1) % 3
                # opponents
                self.move_opponents()
                # model
                model
                Model = model
                if ui_state_mode == 2:
                    # Mode 2: Train NET with Reinforce Learning
                    RL_ind
                    Model = RL_ind.model
                    # save state_now
                    state_now = np.zeros((1, 30))
                    for op in self.opponents:
                        if op.y >= 0 and op.y < CarRaceGame.game_rows:
                            state_now[0][op.y // CarRaceGame.car_height * 5 + op.x // CarRaceGame.car_width] = 1
                    state_now[0][self.player.y // CarRaceGame.car_height * 5 + self.player.x // CarRaceGame.car_width] = .5
                elif ui_state_mode == 3:
                    # Mode 3: Train NET with Evolutive Population
                    ES_ind
                    Model = ES_ind.model
                # player
                game_state_crashed = self.player.move(self.opponents, ui_state_mode, Model)
                if ui_state_mode == 2:
                    # Mode 2: Train NET with Reinforce Learning
                    # save state_next
                    state_next = np.zeros((1, 30))
                    for op in self.opponents:
                        if op.y >= 0 and op.y < CarRaceGame.game_rows:
                            state_next[0][op.y // CarRaceGame.car_height * 5 + op.x // CarRaceGame.car_width] = 1
                    state_next[0][self.player.y // CarRaceGame.car_height * 5 + self.player.x // CarRaceGame.car_width] = .5
                    if game_state_crashed:
                        reward = -1
                    else:
                        reward = get_reward(state_next)
                        if reward == -1:
                            game_state_crashed = True
                    RL_ind.save_itaration(state_now, self.player.x // CarRaceGame.car_width, reward, state_next, False)
                    RL_ind.replay_train()
                print("#----------------------------------------------------------#")

    def draw_game(self):
        pg.draw.rect(screen, self.game_color_bg, pg.Rect(0, 0, CarRaceGame.game_W, CarRaceGame.game_H))
        self.draw_grid()
        self.draw_walls()
        # player
        self.draw_car(self.player.x, self.player.y, self._game_color_player)
        # opponents
        for op in self.opponents:
            if op.x >= 0:
                self.draw_car(op.x, op.y, self._game_color_opponent)


def load_model_file(model_path):
    try:
        model = NET_model.NET_model()
        model.load_model(model_path)
        return model
    except Exception as e:
        print("Model not found: " + model_path)
        exit()


def init_NET(model_path):
    global model
    model = load_model_file(model_path)


def init_ES():
    global ES_population_size
    global ES_seed
    i = 0
    model = load_model_file(model_path)
    ES_seed.append(ES.ES_indiv(model, i))

    global ES_best_score
    ES_best_score = 0
    global ES_population
    ES_population = ES.Population(ES_population_size, ES_seed, True)
    for ind in range(ES_population_size):
        indiv = ES_population.get_indiv(ind)
        indiv.indiv_obj = Player(2 * CarRaceGame.car_width, 5 * CarRaceGame.car_height)
    global ES_ind
    ES_ind = ES_population.get_next_indiv()


def init_RL(reset_RL=False):
    if RL_ind is None or reset_RL:
        model = load_model_file(model_path)
        global RL_ind
        RL_ind = RL.RL_indiv(model, outcome_activation="softmax", batch_size=50, history_size=200, game_over_state=False)
        global RL_best_score
        RL_best_score = 0


class CarRaceUI():

    def __init__(self, CarRace_game):
        # ui vars
        self.playButton = None
        self.speedUpButton = None
        self.speedDownButton = None
        self.modeUpButton = None
        self.modeDownButton = None
        self._game = CarRace_game

        # ui states
        self.ui_state_playButton = "Play"
        self.ui_state_speed = 10
        self.ui_state_mode = 0
        self.ui_state_mode_string = ["Manual", "UseNET", "TrainRL", "TrainES"]

        # init UI
        self.init_ui()

    def write_text(self, surface, text, text_color, length, height, x, y):
        font_size = 2 * int(length // len(text))
        myFont = pg.font.SysFont("Calibri", font_size)
        myText = myFont.render(text, 1, text_color)
        surface.blit(myText, ((x + length / 2) - myText.get_width() / 2, (y + height / 2) - myText.get_height() / 2))
        return surface

    def init_ui(self):
        pg.display.set_caption("Car Race")
        self.playButton = Buttons.Button()
        self.speedUpButton = Buttons.Button()
        self.speedDownButton = Buttons.Button()
        self.modeUpButton = Buttons.Button()
        self.modeDownButton = Buttons.Button()
        # create buttons
        self.playButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 30, 145, 50, 0, self.ui_state_playButton, (255, 255, 255))
        self.speedDownButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
        self.speedUpButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
        self.modeDownButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
        self.modeUpButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))

    def update_ui(self):
        if not self._game.game_state_running:
            self.ui_state_playButton = "Play"
        else:
            self.ui_state_playButton = "Stop"

    def draw_ui(self):
        # play button
        self.playButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 30, 145, 50, 0, self.ui_state_playButton, (255, 255, 255))
        # score
        self.write_text(screen, "Score: " + str(self._game.game_state_score), (107, 142, 35), 145, 40, CarRaceGame.game_W + 10, 100)
        # speed
        self.write_text(screen, "Speed: " + str(self.ui_state_speed), (107, 142, 35), 145, 40, CarRaceGame.game_W + 10, 140)
        if self.ui_state_speed > 1:
            self.speedDownButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
        self.speedUpButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
        # mode
        self.write_text(screen, "Mode: ", (107, 142, 35), 120, 30, CarRaceGame.game_W + 20, 240)
        self.write_text(screen, self.ui_state_mode_string[self.ui_state_mode], (107, 142, 35), 80, 10, CarRaceGame.game_W + 50, 275)
        if not self._game.game_state_running:
            if self.ui_state_mode > 0:
                self.modeDownButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
            if self.ui_state_mode < 3:
                self.modeUpButton.create_button(screen, (107, 142, 35), CarRaceGame.game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))
        # ES info
        if self.ui_state_mode == 2 and self._game.game_state_running:
            self.write_text(screen, "Game: " + str(RL_games_played), (107, 142, 35), 80, 20, 20, CarRaceGame.game_H + 10)
            self.write_text(screen, "Best score:" + str(RL_best_score), (107, 142, 35), 150, 20, 20, CarRaceGame.game_H + 50)
        if self.ui_state_mode == 3 and self._game.game_state_running:
            self.write_text(screen, "Gen: " + str(ES_ind.generation), (107, 142, 35), 60, 20, 20, CarRaceGame.game_H + 10)
            self.write_text(screen, "ID: " + str(ES_ind.indiv_id), (107, 142, 35), 40, 20, 20, CarRaceGame.game_H + 30)
            self.write_text(screen, "Best score:" + str(ES_best_score), (107, 142, 35), 150, 20, 20, CarRaceGame.game_H + 50)


game = CarRaceGame()
ui = CarRaceUI(game)


while not done:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if ui.playButton.pressed(pg.mouse.get_pos()):
                if game.game_state_running:
                    game.game_state_running = False
                else:
                    game.init_game()
                    game.game_state_running = True
            if ui.speedUpButton.pressed(pg.mouse.get_pos()):
                ui.ui_state_speed += 1
            if ui.speedDownButton.pressed(pg.mouse.get_pos()):
                if ui.ui_state_speed > 1:
                    ui.ui_state_speed -= 1
            if not game.game_state_running:
                if ui.modeUpButton.pressed(pg.mouse.get_pos()):
                    if ui.ui_state_mode < 3:
                        ui.ui_state_mode += 1
                if ui.modeDownButton.pressed(pg.mouse.get_pos()):
                    if ui.ui_state_mode > 0:
                        ui.ui_state_mode -= 1
    if game_refresh:
        game.update_game()
    if ui_refresh:
        ui.update_ui()
    game.draw_game()
    ui.draw_ui()
    pg.display.flip()
    clock.tick(ui.ui_state_speed)
