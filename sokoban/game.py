#game.py - Sokoban game logic and main loop
import pygame
import sys
from pygame.locals import *
import constants as SOKOBAN
from level import *
from player import *
from scores import *
from player_interface import *
from solver import *

import _thread
import time


ACTION_TO_KEY = {
    'u': K_UP,   'U': K_UP,
    'd': K_DOWN, 'D': K_DOWN,
    'l': K_LEFT, 'L': K_LEFT,
    'r': K_RIGHT,'R': K_RIGHT,
}


AUTO_MOVE_EVENT = pygame.USEREVENT + 1

_auto_running = False
_auto_cancel  = False

def move(threadName, delay, strategy):
    global _auto_running, _auto_cancel
    _auto_running = True
    _auto_cancel  = False

    for step in strategy:
        if _auto_cancel:
            break
        key = ACTION_TO_KEY.get(step)
        if key is not None:
            evt = pygame.event.Event(KEYDOWN, {'key': key, 'mod': 0, 'unicode': ''})
            pygame.event.post(evt)
        time.sleep(0.25)

    _auto_running = False


class Game:
    def __init__(self, window):
        self.window = window
        self.load_textures()
        self.player = None
        self.index_level = 1
        self.max_level   = 18
        self.load_level()
        self.play = True
        self.scores = Scores(self)
        self.player_interface = PlayerInterface(self.player, self.level)

        self.steps      = 0
        self.start_time = None
        self.elapsed    = 0.0
        self.timer_on   = False

        # Thoi gian chay thuat toan (solver time) - do rieng, luu vao scores
        # Khac voi self.elapsed (thoi gian toan bo tu khi bat dau play den khi thang)
        self.solver_time   = 0.0   # thoi gian solver tinh toan (giay)
        self.nodes_exp     = 0     # so nut da mo rong trong lan giai gan nhat

        self.solve_status   = ""
        self.solve_steps    = 0
        self.current_method = ""

        self.font_hud = pygame.font.Font(
            'sokoban\\assets\\fonts\\FreeSansBold.ttf', 16)
        self.font_big = pygame.font.Font(
            'sokoban\\assets\\fonts\\FreeSansBold.ttf', 22)

    def load_textures(self):
        self.textures = {
            SOKOBAN.WALL:          pygame.image.load('sokoban\\assets\\images\\wall.png').convert_alpha(),
            SOKOBAN.BOX:           pygame.image.load('sokoban\\assets\\images\\box.png').convert_alpha(),
            SOKOBAN.TARGET:        pygame.image.load('sokoban\\assets\\images\\target.png').convert_alpha(),
            SOKOBAN.TARGET_FILLED: pygame.image.load('sokoban\\assets\\images\\valid_box.png').convert_alpha(),
            SOKOBAN.PLAYER:        pygame.image.load('sokoban\\assets\\images\\player_sprites.png').convert_alpha(),
        }

    def load_level(self):
        self.level = Level(self.index_level)
        self.board = pygame.Surface((self.level.width, self.level.height))
        if self.player:
            self.player.pos = self.level.position_player
            self.player_interface.level = self.level
        else:
            self.player = Player(self.level)

        self.steps          = 0
        self.elapsed        = 0.0
        self.timer_on       = False
        self.start_time     = None
        self.solver_time    = 0.0   # reset thoi gian solver khi load level moi
        self.nodes_exp      = 0     # reset so nut mo rong
        self.solve_status   = ""
        self.solve_steps    = 0
        self.current_method = ""

    def start_timer(self):
        if not self.timer_on:
            self.start_time = time.time() - self.elapsed
            self.timer_on   = True

    def stop_timer(self):
        if self.timer_on:
            self.elapsed  = time.time() - self.start_time
            self.timer_on = False

    def update_timer(self):
        if self.timer_on:
            self.elapsed = time.time() - self.start_time

    def start(self):
        clock = pygame.time.Clock()
        while self.play:
            self.update_timer()
            for event in pygame.event.get():
                self.process_event(event)
            self.update_screen()
            clock.tick(60)

    def process_event(self, event):
        global _auto_cancel

        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                self.play = False

            if event.key in [K_UP, K_DOWN, K_LEFT, K_RIGHT, K_z, K_s, K_q, K_d]:
                self.player.move(event.key, self.level, self.player_interface)
                self.steps += 1
                self.start_timer()
                if self.has_win():
                    self.on_win()

            if event.key == K_r and not _auto_running:
                _auto_cancel = True
                self.load_level()

            if event.key == K_l and not _auto_running:
                self.level.cancel_last_move(self.player, self.player_interface)
                if self.steps > 0:
                    self.steps -= 1

            num_keys = {
                K_1:1, K_2:2, K_3:3, K_4:4, K_5:5,
                K_6:6, K_7:7, K_8:8, K_9:9, K_0:10,
            }
            if event.key in num_keys:
                _auto_cancel = True
                time.sleep(0.05)
                self.index_level = num_keys[event.key]
                self.load_level()

            if event.key == K_PAGEUP:
                _auto_cancel = True
                time.sleep(0.05)
                self.index_level = max(1, self.index_level - 1)
                self.load_level()
            if event.key == K_PAGEDOWN:
                _auto_cancel = True
                time.sleep(0.05)
                self.index_level = min(18, self.index_level + 1)
                self.load_level()

            if event.key == K_n:
                _auto_cancel = True
                time.sleep(0.05)
                self.index_level = min(18, self.index_level + 1)
                self.load_level()

        if event.type == MOUSEBUTTONUP:
            self.player_interface.click(event.pos, self.level, self)
        if event.type == MOUSEMOTION:
            self.player_interface.mouse_pos = event.pos

    def update_screen(self):
        pygame.draw.rect(self.board,  SOKOBAN.WHITE,
                         (0, 0, self.level.width * SOKOBAN.SPRITESIZE,
                          self.level.height * SOKOBAN.SPRITESIZE))
        pygame.draw.rect(self.window, SOKOBAN.WHITE,
                         (0, 0, SOKOBAN.WINDOW_WIDTH, SOKOBAN.WINDOW_HEIGHT))

        self.level.render(self.board, self.textures)
        self.player.render(self.board, self.textures)

        pox_x_board = (SOKOBAN.WINDOW_WIDTH / 2)  - (self.board.get_width()  / 2)
        pos_y_board = (SOKOBAN.WINDOW_HEIGHT / 2) - (self.board.get_height() / 2)
        self.window.blit(self.board, (pox_x_board, pos_y_board))

        self.player_interface.render(self.window, self.index_level)
        self._render_hud()

        pygame.display.flip()

    def _render_hud(self):
        pad_x, pad_y = 10, SOKOBAN.WINDOW_HEIGHT - 165
        bg_rect = pygame.Rect(pad_x - 5, pad_y - 5, 295, 160)
        pygame.draw.rect(self.window, (240, 240, 240), bg_rect)
        pygame.draw.rect(self.window, SOKOBAN.BLACK,   bg_rect, 1)

        self._hud_text(f"Level   : {self.index_level} / 18",   pad_x, pad_y)
        method_disp = self.current_method.upper() if self.current_method else "MANUAL"
        self._hud_text(f"Mode    : {method_disp}",              pad_x, pad_y + 18)
        self._hud_text(f"Steps   : {self.steps}",               pad_x, pad_y + 36)
        self._hud_text(f"Time    : {self.elapsed:.1f} s",       pad_x, pad_y + 54)

        # Hien thi thoi gian chay solver (chi co gia tri khi dung auto mode)
        if self.solver_time > 0:
            self._hud_text(f"Solve t : {self.solver_time:.2f} s",
                           pad_x, pad_y + 72, color=(0, 120, 60))
            self._hud_text(f"Nodes   : {self.nodes_exp}",
                           pad_x, pad_y + 90, color=(0, 120, 60))
        else:
            self._hud_text(f"Solve t : ---",  pad_x, pad_y + 72)
            self._hud_text(f"Nodes   : ---",  pad_x, pad_y + 90)

        best_time, best_steps = self.scores.get_best(self.index_level)
        bt_str = f"{best_time:.1f}s" if best_time is not None else "---"
        bs_str = str(best_steps)     if best_steps is not None else "---"
        self._hud_text(f"Best    : {bs_str} steps / {bt_str}",
                       pad_x, pad_y + 108, color=(0, 100, 180))

        status_color_map = {
            "SOLVING...":  SOKOBAN.BLUE,
            "SOLVED":      (0, 150, 0),
            "NO SOLUTION": (200, 0, 0),
            "TIMEOUT":     (200, 100, 0),
        }
        color = status_color_map.get(self.solve_status, SOKOBAN.BLACK)
        status_text = self.solve_status if self.solve_status else "READY"
        self._hud_text(f"Status  : {status_text}", pad_x, pad_y + 126, color=color)

        font11 = pygame.font.Font('sokoban\\assets\\fonts\\FreeSansBold.ttf', 11)
        self.window.blit(
            font11.render("N=Next  R=Restart  L=Undo  PgUp/PgDn=Level",
                          True, SOKOBAN.GREY),
            (pad_x, pad_y + 144)
        )

    def _hud_text(self, text, x, y, color=SOKOBAN.BLACK):
        surf = self.font_hud.render(text, True, color, (240, 240, 240))
        self.window.blit(surf, (x, y))

    def has_win(self):
        nb_missing_target = 0
        for y in range(len(self.level.structure)):
            for x in range(len(self.level.structure[y])):
                if self.level.structure[y][x] == SOKOBAN.TARGET:
                    nb_missing_target += 1
        return nb_missing_target == 0

    def on_win(self):
        self.stop_timer()
        self.solve_status = "SOLVED"
        self.scores.save()   # save() se dung self.solver_time da duoc luu san
        self.index_level += 1
        if self.index_level == 17:
            self.index_level = 1
        self.load_level()

    def auto_move(self, method='dfs'):
        """
        Giai tu dong level hien tai bang thuat toan duoc chi dinh.
        Luong chay:
          1. Reset ban do
          2. Hien thi "SOLVING..."
          3. Goi get_move() -> nhan ve (strategy, solver_time, nodes_expanded)
          4. Luu solver_time vao self.solver_time de:
             - Hien thi len HUD
             - scores.save() se su dung khi player thang
          5. Phat lai tung buoc qua pygame events
        """
        global _auto_cancel
        _auto_cancel = True
        time.sleep(0.1)

        self.current_method = method
        self.solve_status   = "SOLVING..."
        self.solve_steps    = 0
        self.solver_time    = 0.0   # reset truoc khi goi solver
        self.nodes_exp      = 0
        self.update_screen()
        pygame.display.flip()

        TIMEOUT = 4000
        t0 = time.time()

        try:
            # get_move() tra ve tuple (strategy, elapsed_solve, nodes_expanded)
            # elapsed_solve: thoi gian thuat toan chay (giay) - do bang time() trong solver
            # nodes_expanded: so nut da mo rong trong qua trinh tim kiem
            result = get_move(
                self.level.structure[:-1],
                self.level.position_player,
                method
            )
            # Giai pack ket qua tra ve
            strategy, elapsed_solve, nodes_exp = result

        except Exception as e:
            strategy     = None
            elapsed_solve = 0.0
            nodes_exp     = 0
            print(f"Solver error: {e}")

        wall_time = time.time() - t0   # tong thoi gian thuc tu khi goi den khi xong

        # Luu thoi gian solver va so nut vao bien thanh vien
        # De scores.save() va HUD co the su dung
        self.solver_time = round(elapsed_solve, 3)
        self.nodes_exp   = nodes_exp

        if wall_time >= TIMEOUT:
            self.solve_status = "TIMEOUT"
            print(f"[{method.upper()}] TIMEOUT ({wall_time:.1f}s)")
            return

        if not strategy:
            self.solve_status = "NO SOLUTION"
            print(f"[{method.upper()}] NO SOLUTION found")
            return

        self.solve_status = "SOLVED"
        self.solve_steps  = len(strategy)
        self.start_timer()
        print(f"[{method.upper()}] {len(strategy)} steps | "
              f"solver: {elapsed_solve:.2f}s | nodes: {nodes_exp}")

        _auto_cancel = False
        try:
            _thread.start_new_thread(move, ("Thread-1", 2, strategy))
        except Exception as e:
            print(f"Error: unable to start thread: {e}")