from sys import argv
import pygame as pg
import numpy as np
from car_race_RLreward import get_reward
import Buttons
import NET_model
import ES
import RL
import json

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
        self.last_x = -1
        self.next_x = -1

    def move(self, opponents, mode, Model):
        board = np.zeros((1, 30))
        move_enable = False
        for op in opponents:
            if op.y >= 0 and op.y < CarRace.game_rows:
                if op.y % CarRace.car_height == 0:
                    move_enable = True
                board[0][op.y // CarRace.car_height * 5 + op.x // CarRace.car_width] = 1
        self.next_x = self.x
        board[0][self.y // CarRace.car_height * 5 + self.x // CarRace.car_width] = .5
        if mode == 0:
            # Mode 0: Manual game
            self._manual()
            multi_steps = False
        elif mode == 2:
            # Mode 2: Train NET with Reinforce Learning
            # if np.random.random() > 0.95:  # percentage to take random action
            if False:  # force to predict action
                if move_enable:
                    self.next_x = np.random.randint(5) * CarRace.car_width
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
        self.last_x = self.x
        crashed = self.check_crash(opponents)
        if not crashed:
            if multi_steps:
                while self.next_x != self.x:
                    if self.next_x < self.x:
                        self.x -= CarRace.car_width
                        print("<--")
                    else:
                        self.x += CarRace.car_width
                        print("-->")
                    crashed = self.check_crash(opponents)
                    if crashed:
                        break
            else:
                if self.next_x < self.x:
                    print("<--")
                elif self.next_x > self.x:
                    print("-->")
                self.x = self.next_x
                crashed = self.check_crash(opponents)
        # if crash, return False
        return crashed

    def check_crash(self, opponents):
        for op in opponents:
            if np.absolute(op.x - self.x) < CarRace.car_width and np.absolute(op.y - self.y) < CarRace.car_height:
                return True
        return False

    def _manual(self):
        pressed = pg.key.get_pressed()
        if pressed[pg.K_LEFT]:
            if self.x > 0:
                self.next_x = self.x - CarRace.car_width
        elif pressed[pg.K_RIGHT]:
            if self.x < 12:
                self.next_x = self.x + CarRace.car_width

    def _network(self, board, Model):
        pred = Model.predict(board)
        self.next_x = np.argmax(pred[0]) * CarRace.car_width


class CarRace:

    game_cols = 21
    game_rows = 24
    game_H = 384
    block_size = game_H / game_rows  # block size 16
    game_W = game_cols * block_size
    car_width = 3
    car_height = 4

    def __init__(self, model_path="./pre_train_models/NET_model.h5"):
        # NET
        self.model_path = model_path
        self.model = None
        self.model_pred_enable = False
        self.NET_history = []

        # ES
        self.ES_population_size = 10
        self.ES_population = None
        self.ES_ind = None
        self.ES_is_running = False
        self.ES_seed = []
        self.ES_best_score = 0
        self.ES_history = []

        # RL
        self.RL_ind = None
        self.RL_best_score = 0
        self.RL_games_played = 0
        self.RL_history = []

        # game vars
        self.grid_line_W = 2
        self.walls_state = 0  # 0, 1 or 2
        self.opponents_number = 6
        self.opponents = []
        self.player = None

        # game colors
        self.game_color_bg = (255, 255, 255)  # "#FFFFFF"
        self.game_color_line = (221, 221, 221)  # "#DDDDDD"
        self.game_color_wall = (85, 85, 85)  # "#555555"
        self.game_color_opponent = (0, 0, 0)  # "#000000"
        self.game_color_player = (92, 150, 24)  # "#5c9618"
        self.game_color_player_ = (48, 74, 18)  # "#304a12"

        # game states
        self.game_state_multi_steps = False
        self.game_state_score = 0
        self.game_state_crashed = False
        self.game_state_running = False

        # ui vars
        self.playButton = None
        self.speedUpButton = None
        self.speedDownButton = None
        self.modeUpButton = None
        self.modeDownButton = None

        # ui states
        self.ui_state_playButton = "Play"
        self.ui_state_speed = 10
        self.ui_state_mode = 0
        self.ui_state_mode_string = ["Manual", "UseNET", "TrainRL", "TrainES"]

        self.init_game()
        self.init_ui()

    def load_model_file(self, model_path):
        try:
            model = NET_model.NET_model()
            model.load_model(self.model_path)
            return model
        except Exception as e:
            print("Model not found: " + self.model_path)
            exit()

    def init_NET(self, model_path):
        self.model = self.load_model_file(self.model_path)

    def init_ES(self):
        i = 0
        model = self.load_model_file(self.model_path)
        self.ES_seed.append(ES.ES_indiv(model, i))
        self.ES_best_score = 0
        self.ES_population = ES.Population(self.ES_population_size, self.ES_seed, True)
        for ind in range(self.ES_population_size):
            indiv = self.ES_population.get_indiv(ind)
            indiv.indiv_obj = Player(2 * CarRace.car_width, 5 * CarRace.car_height)
        self.ES_ind = self.ES_population.get_next_indiv()

    def init_RL(self, reset_RL=False):
        if self.RL_ind is None or reset_RL:
            model = self.load_model_file(self.model_path)
            self.RL_ind = RL.RL_indiv(model, outcome_activation="relu", batch_size=50, history_size=200, game_over_state=False)
            self.RL_best_score = 0
        else:
            if self.RL_best_score == self.game_state_score:
                self.RL_ind.model.save_model("save_models/RL_fit{:0>3}.h5".format(self.game_state_score))

    def save_history(self, mode):
        # Mode 1: Run Trained NET
        if mode == 1:
            self.NET_history.append({'index': len(self.NET_history), 'score': self.game_state_score})
        # Mode 2: Train NET with Reinforce Learning
        elif mode == 2:
            self.RL_history.append({'index': len(self.RL_history), 'score': self.game_state_score})
        # Mode 3: Train NET with Evolutive Population
        elif mode == 3:
            self.ES_history.append({'index': len(self.ES_history), 'score': self.game_state_score, 'gen': self.ES_ind.generation, 'ind_id': self.ES_ind.indiv_id})

    def draw_grid(self):
        for i in range(CarRace.game_cols + 1):
            pg.draw.line(screen, self.game_color_line, (CarRace.block_size * i, 0), (CarRace.block_size * i, CarRace.game_H), self.grid_line_W)
        for i in range(CarRace.game_rows + 1):
            pg.draw.line(screen, self.game_color_line, (0, CarRace.block_size * i), (CarRace.game_W, CarRace.block_size * i), self.grid_line_W)

    def draw_rect(self, x, y, rect_color):
        if y < CarRace.game_rows:
            pg.draw.rect(screen, rect_color, pg.Rect(x * CarRace.block_size + self.grid_line_W, y * CarRace.block_size + self.grid_line_W, CarRace.block_size - self.grid_line_W, CarRace.block_size - self.grid_line_W))
            pg.draw.rect(screen, (255, 255, 255), pg.Rect(x * CarRace.block_size + self.grid_line_W + 1, y * CarRace.block_size + self.grid_line_W + 1, CarRace.block_size - self.grid_line_W - 2, CarRace.block_size - self.grid_line_W - 2))
            pg.draw.rect(screen, rect_color, pg.Rect(x * CarRace.block_size + 2 * self.grid_line_W, y * CarRace.block_size + 2 * self.grid_line_W, CarRace.block_size - 3 * self.grid_line_W, CarRace.block_size - 3 * self.grid_line_W))

    def draw_car(self, x, y, car_color):
        x += CarRace.car_width  # left wall offset
        self.draw_rect(x + 1, y, car_color)
        self.draw_rect(x + 1, y + 1, car_color)
        self.draw_rect(x + 1, y + 2, car_color)
        self.draw_rect(x, y + 1, car_color)
        self.draw_rect(x + 2, y + 1, car_color)
        self.draw_rect(x, y + 3, car_color)
        self.draw_rect(x + 2, y + 3, car_color)

    def draw_walls(self):
        state = self.walls_state
        for i in range(CarRace.game_rows):
            if state < 2:
                self.draw_rect(1, i, self.game_color_wall)
                self.draw_rect(CarRace.game_cols - 2, i, self.game_color_wall)
            state = (state + 1) % 3

    def shuffle_needed(self):
        for i in range(len(self.opponents) - 1):
            for j in range(i + 1, len(self.opponents)):
                if self.opponents[j].x == self.opponents[i].x and np.absolute(self.opponents[j].y - self.opponents[i].y) < 2 * CarRace.car_height:
                    return True
                if self.opponents[j].y == self.opponents[i].y and np.absolute(self.opponents[j].x - self.opponents[i].x) <= CarRace.car_width:
                    return True
        ###
        # check for holes in creasent diagonals (right and left diags) for each opponent
        aux_grid = np.zeros(shape=(1, 30), dtype=float)
        for op in self.opponents:
            if op.y < 0 and op.y > -CarRace.game_rows:
                aux_grid[0][(op.y + CarRace.game_rows) // CarRace.car_height * 5 + op.x // CarRace.car_width] = 1
        while get_reward(aux_grid) == -1:
            ###
            # delete diagonal self.opponents
            index = np.random.randint(0, len(self.opponents))
            if self.opponents[index].y < 0:
                self.opponents[index].y -= CarRace.car_height * 2
            aux_grid = np.zeros(shape=(1, 30), dtype=float)
            for op in self.opponents:
                if op.y < 0 and op.y > -CarRace.game_rows:
                    aux_grid[0][(op.y + CarRace.game_rows) // CarRace.car_height * 5 + op.x // CarRace.car_width] = 1
        return False

    def move_opponents(self):
        for op in self.opponents:
            if op.y < CarRace.game_rows:
                op.y += 1
            else:
                self.game_state_score += 1
                op.x = np.random.randint(5) * CarRace.car_width
                op.y -= CarRace.car_height * 8 - 1
        deadlock = 0
        while self.shuffle_needed():
            if deadlock > 10:
                print("Deadlock unsolve")
                self.game_state_crashed = True
                break
            deadlock += 1
            for i in range(len(self.opponents) - 1):
                for j in range(i + 1, len(self.opponents)):
                    while self.opponents[j].y == self.opponents[i].y and np.absolute(self.opponents[j].x - self.opponents[i].x) <= CarRace.car_width:
                        if np.random.random() > 0.5:
                            self.opponents[j].x = np.random.randint(5) * CarRace.car_width
                        else:
                            self.opponents[j].y -= CarRace.car_height
                    while self.opponents[j].x == self.opponents[i].x and np.absolute(self.opponents[j].y - self.opponents[i].y) < 2 * CarRace.car_height:
                        self.opponents[j].y -= CarRace.car_height

    def init_game(self):
        pg.draw.rect(screen, self.game_color_bg, pg.Rect(0, 0, CarRace.game_W, CarRace.game_H))
        self.draw_grid()
        self.draw_walls()
        # set mode
        # Mode 1: Run Trained NET
        if self.ui_state_mode == 1:
            self.init_NET(self.model_path)
        # Mode 2: Train NET with Reinforce Learning
        elif self.ui_state_mode == 2:
            if self.game_state_score > self.RL_best_score:
                self.RL_best_score = self.game_state_score
            self.init_RL()
        # Mode 3: Train NET with Evolutive Population
        elif self.ui_state_mode == 3:
            if self.ES_is_running:
                if self.game_state_score > self.ES_best_score:
                    self.ES_best_score = self.game_state_score
                self.ES_ind.fitness = self.game_state_score
                self.ES_ind = self.ES_population.get_next_indiv()
            else:
                self.ES_is_running = True
                self.init_ES()
        # self.player
        self.player = Player(2 * CarRace.car_width, 5 * CarRace.car_height)
        self.draw_car(self.player.x, self.player.y, self.game_color_player)
        # self.opponents
        self.opponents = []
        # if self.opponents are located completely random, could cause deadlock
        # for i in range(self.opponents_number):
        #     self.opponents.append(Position(np.random.randint(4) * CarRace.car_width, -CarRace.car_height * np.random.randint(1, i + 2)))
        # to solve initial deadlock, positions are not fully random
        self.opponents.append(Position(0 * CarRace.car_width, -CarRace.car_height * np.random.randint(1, 3)))
        self.opponents.append(Position(0 * CarRace.car_width, -CarRace.car_height * np.random.randint(3, 5)))
        self.opponents.append(Position(2 * CarRace.car_width, -CarRace.car_height * np.random.randint(1, 3)))
        self.opponents.append(Position(2 * CarRace.car_width, -CarRace.car_height * np.random.randint(3, 5)))
        self.opponents.append(Position(4 * CarRace.car_width, -CarRace.car_height * np.random.randint(1, 3)))
        self.opponents.append(Position(4 * CarRace.car_width, -CarRace.car_height * np.random.randint(3, 5)))
        # insert diagonal of self.opponents
        # self.opponents.append(Position(3 * CarRace.car_width, -CarRace.car_height * 2))
        # self.opponents.append(Position(4 * CarRace.car_width, -CarRace.car_height * 1))
        # self.opponents.append(Position(2 * CarRace.car_width, -CarRace.car_height * 3))
        # self.opponents.append(Position(1 * CarRace.car_width, -CarRace.car_height * 4))
        # self.opponents.append(Position(0 * CarRace.car_width, -CarRace.car_height * 5))
        # self.opponents.append(Position(3 * CarRace.car_width, -CarRace.car_height * 8))
        # game_state_vars
        self.game_state_score = 0
        self.game_state_crashed = False

    def update_game(self):
        if self.game_state_crashed:
            self.save_history(self.ui_state_mode)
            if self.ui_state_mode == 2:
                self.init_game()
                self.RL_games_played += 1
            elif self.ui_state_mode == 3:
                self.init_game()
            else:
                self.game_state_running = False
                self.game_state_crashed = False
        else:
            if self.game_state_running:
                # walls
                self.walls_state = (self.walls_state + 1) % 3
                # self.opponents
                self.move_opponents()
                # model
                Model = self.model
                if self.ui_state_mode == 2:
                    # Mode 2: Train NET with Reinforce Learning
                    Model = self.RL_ind.model
                    # save state_now
                    state_now = np.zeros((1, 30))
                    for op in self.opponents:
                        if op.y >= 0 and op.y < CarRace.game_rows:
                            state_now[0][op.y // CarRace.car_height * 5 + op.x // CarRace.car_width] = 1
                    state_now[0][self.player.y // CarRace.car_height * 5 + self.player.x // CarRace.car_width] = .5
                elif self.ui_state_mode == 3:
                    # Mode 3: Train NET with Evolutive Population
                    Model = self.ES_ind.model
                # self.player
                self.game_state_crashed = self.player.move(self.opponents, self.ui_state_mode, Model)
                if self.ui_state_mode == 2:
                    # Mode 2: Train NET with Reinforce Learning
                    # save state_next
                    state_next = np.zeros((1, 30))
                    for op in self.opponents:
                        if op.y >= 0 and op.y < CarRace.game_rows:
                            state_next[0][op.y // CarRace.car_height * 5 + op.x // CarRace.car_width] = 1
                    state_next[0][self.player.y // CarRace.car_height * 5 + self.player.x // CarRace.car_width] = .5
                    if self.game_state_crashed:
                        reward = -1
                    else:
                        reward = get_reward(state_next)
                        if reward == -1:
                            self.game_state_crashed = True
                    self.RL_ind.save_itaration(state_now, self.player.x // CarRace.car_width, reward, state_next, False)
                    self.RL_ind.replay_train()
                print("#----------------------------------------------------------#")

    def draw_game(self):
        pg.draw.rect(screen, self.game_color_bg, pg.Rect(0, 0, CarRace.game_W, CarRace.game_H))
        self.draw_grid()
        self.draw_walls()
        # self.player
        self.draw_car(self.player.x, self.player.y, self.game_color_player)
        # self.opponents
        for op in self.opponents:
            if op.x >= 0:
                self.draw_car(op.x, op.y, self.game_color_opponent)

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
        self.playButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 30, 145, 50, 0, self.ui_state_playButton, (255, 255, 255))
        self.speedDownButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
        self.speedUpButton.create_button(screen, (107, 142, 35), CarRace.game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
        self.modeDownButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
        self.modeUpButton.create_button(screen, (107, 142, 35), CarRace.game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))

    def update_ui(self):
        if not self.game_state_running:
            self.ui_state_playButton = "Play"
        else:
            self.ui_state_playButton = "Stop"

    def draw_ui(self):
        # play button
        self.playButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 30, 145, 50, 0, self.ui_state_playButton, (255, 255, 255))
        # score
        self.write_text(screen, "Score: " + str(self.game_state_score), (107, 142, 35), 145, 40, CarRace.game_W + 10, 100)
        # speed
        self.write_text(screen, "Speed: " + str(self.ui_state_speed), (107, 142, 35), 145, 40, CarRace.game_W + 10, 140)
        if self.ui_state_speed > 1:
            self.speedDownButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 180, 65, 40, 0, "<", (255, 255, 255))
        self.speedUpButton.create_button(screen, (107, 142, 35), CarRace.game_W + 90, 180, 65, 40, 0, ">", (255, 255, 255))
        # mode
        self.write_text(screen, "Mode: ", (107, 142, 35), 120, 30, CarRace.game_W + 20, 240)
        self.write_text(screen, self.ui_state_mode_string[self.ui_state_mode], (107, 142, 35), 80, 10, CarRace.game_W + 50, 275)
        if not self.game_state_running:
            if self.ui_state_mode > 0:
                self.modeDownButton.create_button(screen, (107, 142, 35), CarRace.game_W + 10, 300, 65, 40, 0, "<", (255, 255, 255))
            if self.ui_state_mode < 3:
                self.modeUpButton.create_button(screen, (107, 142, 35), CarRace.game_W + 90, 300, 65, 40, 0, ">", (255, 255, 255))
        # ES info
        if self.ui_state_mode == 2 and self.game_state_running:
            self.write_text(screen, "Game: " + str(self.RL_games_played), (107, 142, 35), 80, 20, 20, CarRace.game_H + 10)
            self.write_text(screen, "Best score:" + str(self.RL_best_score), (107, 142, 35), 150, 20, 20, CarRace.game_H + 50)
        if self.ui_state_mode == 3 and self.game_state_running:
            self.write_text(screen, "Gen: " + str(self.ES_ind.generation), (107, 142, 35), 60, 20, 20, CarRace.game_H + 10)
            self.write_text(screen, "ID: " + str(self.ES_ind.indiv_id), (107, 142, 35), 40, 20, 20, CarRace.game_H + 30)
            self.write_text(screen, "Best score:" + str(self.ES_best_score), (107, 142, 35), 150, 20, 20, CarRace.game_H + 50)


if len(argv) < 2:  # load path from args
    game = CarRace()
else:
    game = CarRace(argv[1])

while not done:
    screen.fill((0, 0, 0))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            done = True
        elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            done = True
        elif event.type == pg.MOUSEBUTTONDOWN:
            if game.playButton.pressed(pg.mouse.get_pos()):
                if game.game_state_running:
                    game.game_state_running = False
                else:
                    game.init_game()
                    game.game_state_running = True
            if game.speedUpButton.pressed(pg.mouse.get_pos()):
                game.ui_state_speed += 1
            if game.speedDownButton.pressed(pg.mouse.get_pos()):
                if game.ui_state_speed > 1:
                    game.ui_state_speed -= 1
            if not game.game_state_running:
                if game.modeUpButton.pressed(pg.mouse.get_pos()):
                    if game.ui_state_mode < 3:
                        game.ui_state_mode += 1
                if game.modeDownButton.pressed(pg.mouse.get_pos()):
                    if game.ui_state_mode > 0:
                        game.ui_state_mode -= 1
    if game_refresh:
        game.update_game()
    if ui_refresh:
        game.update_ui()
    game.draw_game()
    game.draw_ui()
    pg.display.flip()
    clock.tick(game.ui_state_speed)

with open('stats/NET_history.json', 'w') as outNET:
    json.dump(game.NET_history, outNET)
with open('stats/ES_history.json', 'w') as outES:
    json.dump(game.ES_history, outES)
with open('stats/RL_history.json', 'w') as outRL:
    json.dump(game.RL_history, outRL)
