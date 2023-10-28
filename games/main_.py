import sys
import pygame
from typing import List, Tuple
import cv2
from math import *
from pygame import gfxdraw
import random
from time import time
import numpy as np
from common.handTracker import handTracker
from common.ws_client import WebSocketClient
from time import sleep
from threading import Thread

on_config = False
print_pos = False


# https://github.com/fandhikazhr/handDetector

def get_opencv_img_res(opencv_image):
    height, width = opencv_image.shape[:2]
    return width, height


def convert_opencv_img_to_pygame(opencv_image):
    """
        Convertir des images OpenCV pour Pygame.
        see https:#blanktar.jp/blog/2016/01/pygame-draw-opencv-image.html
    """
    # Puisque OpenCV est BGR et pygame est RVB, il est nécessaire de le convertir.
    opencv_image = opencv_image[:, :, ::-1]
    # OpenCV(la taille,largeur,Nombre de couleurs), Pygame(largeur, la taille)Donc, cela est également converti.
    shape = opencv_image.shape[1::-1]
    pygame_image = pygame.image.frombuffer(opencv_image.tostring(), shape, 'RGB')
    return pygame_image


def draw_text(sc, text, x, y, color=(200, 100, 200), size=12, font_name=None, align="nw"):
    font = pygame.font.Font(font_name or pygame.font.get_default_font(), size)
    text_surface = font.render(str(text), True, color)
    text_rect = text_surface.get_rect()
    if align == "nw":
        text_rect.topleft = (x, y)
    if align == "ne":
        text_rect.topright = (x, y)
    if align == "sw":
        text_rect.bottomleft = (x, y)
    if align == "se":
        text_rect.bottomright = (x, y)
    if align == "n":
        text_rect.midtop = (x, y)
    if align == "s":
        text_rect.midbottom = (x, y)
    if align == "e":
        text_rect.midright = (x, y)
    if align == "w":
        text_rect.midleft = (x, y)
    if align == "center":
        text_rect.center = (x, y)
    sc.blit(text_surface, text_rect)


# точка пересечения двух отрезков
def cross(line0: List[List[float]], line1: List[List[float]]) -> Tuple[float, float]:
    x0_0, y0_0 = line0[0]
    x0_1, y0_1 = line0[1]
    x1_0, y1_0 = line1[0]
    x1_1, y1_1 = line1[1]

    d = (x0_1 - x0_0) * (y1_1 - y1_0) - (x1_1 - x1_0) * (y0_1 - y0_0)
    if d == 0:
        return  # отрезки параллельны

    t = ((x1_0 - x0_0) * (y1_1 - y1_0) - (y1_0 - y0_0) * (x1_1 - x1_0)) / d
    u = -((x0_0 - x1_0) * (y0_1 - y0_0) - (y0_0 - y1_0) * (x0_1 - x0_0)) / d

    if 0 <= t <= 1 and 0 <= u <= 1:
        x = x0_0 + t * (x0_1 - x0_0)
        y = y0_0 + t * (y0_1 - y0_0)
        return x, y

    return  # отрезки не пересекаются


def xor(a, b):
    return bool(a) != bool(b)


def changColor(image, color):
    colouredImage = pygame.Surface(image.get_size())
    colouredImage.fill(color)

    finalImage = image.copy()
    finalImage.blit(colouredImage, (0, 0), special_flags=pygame.BLEND_MULT)
    return finalImage


class Starfield:
    count = 1000

    def __init__(self, screen):
        self.screen = screen
        self.stars = []
        self.angle = 0
        w = self.screen.get_width()
        h = self.screen.get_height()
        cx = w
        cy = h
        r_min = int(sqrt((cx - w) ** 2 + (cy - h) ** 2)) + 120
        r_max = int(sqrt((cx - 0) ** 2 + (cy - 0) ** 2))
        print(r_min, r_max)
        for i in range(self.count):
            self.stars.append([
                cx + random.randrange(-50, 50),  # x
                cy + random.randrange(-50, 50),  # y
                1 / random.randrange(20, 40),  # speed
                random.randrange(1, 3),  # size
                random.randint(r_min, r_max),  # r
                random.randint(0, 360),  # angle
                random.randint(160, 230)  # color
            ])

    def draw(self):
        for i, star in enumerate(self.stars):
            x, y, speed, size, r, angle, color = star
            star[5] = (angle - speed) % 360

            gfxdraw.filled_circle(self.screen,
                                  int(x + r * sin(radians(angle))),
                                  int(y + r * cos(radians(angle))),
                                  int(size),
                                  (color, color, color))
            # gfxdraw.aacircle(self.screen,
            #                  int(x + r * sin(radians(angle))),
            #                  int(y + r * cos(radians(angle))),
            #                  int(size * 2),
            #                  (color, color, color, 100))
            gfxdraw.filled_circle(self.screen,
                                  int(x + r * sin(radians(angle))),
                                  int(y + r * cos(radians(angle))),
                                  int(size * 3),
                                  (color, color, color, 30))


class SpriteAnimation:
    color = 1

    def __init__(self, filename, width, height, frames_count=1, frame_start=0, frames_per_row=1,
                 frames_per_col=1, current_frame=None, fps=None, angle=0, scale=1):
        self.frames_count = frames_count  # количество кадров в анимации
        self.current_frame = current_frame if current_frame is not None else random.randint(0, frames_count - 1)
        self.frame_start = frame_start  # начальный кадр анимации (например, если анимация начинается с 5 кадра)
        self.image = pygame.image.load(filename)

        self.width = width  # размеры кадра
        self.height = height  # размеры кадра
        self.base_angle = angle
        self.frames_per_row = frames_per_row
        self.frames_per_col = frames_per_col

        self.fps = fps if fps is not None else random.randint(5, 12)
        self.last_frame_time = 0
        self.scale = scale

    def draw(self, screen, x, y, angle):
        frame_x = ((self.current_frame + self.frame_start) % self.frames_per_row) * self.width
        frame_y = ((self.current_frame + self.frame_start) // self.frames_per_row) * self.height

        frame_rect = pygame.Rect(frame_x, frame_y, self.width, self.height)

        image = self.image.subsurface(frame_rect)

        if self.scale != 1:
            image = pygame.transform.scale(image, (int(self.width * self.scale), int(self.height * self.scale)))

        # поворачиваем изображение
        rotated_img = pygame.transform.rotate(image, angle + self.base_angle)

        # определяем прямоугольник отрисовки
        w, h = rotated_img.get_size()
        draw_x = x - w / 2  # + self.origin_x
        draw_y = y - h / 2  # + self.origin_y

        if self.color != -1:
            color = pygame.Color(0)
            color.hsla = (self.color, 50, 50, 100)
            rotated_img = changColor(rotated_img, color)

        # отрисовываем
        screen.blit(rotated_img, (draw_x, draw_y))

    def update(self, ):
        current_time = time()
        time_since_last_frame = current_time - self.last_frame_time

        if time_since_last_frame > 1.0 / self.fps:
            self.current_frame += 1
            if self.current_frame >= self.frames_count:
                self.current_frame = 0

            self.last_frame_time = current_time


class Sputnik:
    size = 50  # размер зеркала спутника
    power: int  # мощность спутника (длина луча)
    is_hover = 0
    active = False
    angle = 90
    angle_extr = (0, 180)
    speed = 3 / 10
    lines_pos = ([0, 0], [0, 0])
    click_pos = (0, 0)
    game_run = False
    colors = [3, -1]

    can_active = 0

    def __init__(self, x, y, power=420, angle=90, active=False, mode=0, delta_angel=60, scale=None, user_angle=None,
                 filename='sprite_sat4.png', img_params=None):
        self.x = x
        self.y = y
        self.power = power
        self.active = active or on_config
        self.angle = angle
        self.angle_def = angle
        self.user_angle = user_angle
        self.angle_extr = (angle - delta_angel, angle + delta_angel)
        self.mode = mode

        scale = scale or scale if scale is not None else random.random() * 0.2 + 0.4
        self.size = int(self.size * scale)

        img_params = img_params or {'width': 850 / 4, 'height': 630 / 4,
                                    'angle': 90,
                                    'frames_count': 36, 'frame_start': 0,
                                    'frames_per_col': 6, 'frames_per_row': 6}
        self.sprite = SpriteAnimation(f"img/{filename}", **img_params, scale=scale)
        self.sprite.color = self.colors[self.active]

    def set_active(self, st):
        self.active = st
        self.sprite.color = self.colors[self.active]

    def take(self, is_user, is_this):
        if self.game_run:
            d_angel = 30 if is_user else 60
            direct = (random.randint(0, 1) * 2 - 1)
            if xor(is_user, is_this):
                self.angle = self.user_angle + direct * d_angel
            else:
                self.angle = self.angle_def + direct * d_angel
            self.speed = -direct * abs(self.speed)

    def rotate(self, d):
        self.angle += d
        if not self.active:
            return
        # if self.angle > self.angle_extr[1]:
        #     self.angle = self.angle_extr[1]
        # if self.angle < self.angle_extr[0]:
        #     self.angle = self.angle_extr[0]

    def update(self):

        a = radians(self.angle)
        dx = self.size * sin(a)
        dy = self.size * cos(a)
        lines_pos = [
            ([self.x - dy * 2, self.y + dx * 2], [self.x + dy * 2, self.y - dx * 2]),
            ([self.x + dx, self.y + dy], [self.x - dx, self.y - dy]),
            ([self.x, self.y], [self.x + dy * 2, self.y - dx * 2]),
        ]
        self.lines_pos = lines_pos
        self.sprite.update()

    def draw(self, sc):
        if self.active:
            hover = self.is_hover
        else:
            hover = 3
            if abs(self.angle - self.angle_def) > abs(self.speed) * .9:
                self.angle += self.speed
                if self.angle > 360:
                    self.angle -= 360
                if self.angle < 0:
                    self.angle += 360
            else:
                self.angle = self.angle_def

        if hover == 1:
            color = [(50, 150, 100), (0, 200, 150), (50, 255, 50), (150, 0, 0)][hover]
            size = 1.8 * self.size
            pygame.draw.polygon(sc, color,
                                [[self.x - size, self.y - size], [self.x - size, self.y + size],
                                 [self.x + size, self.y + size], [self.x + size, self.y - size]],
                                width=5)
        if print_pos:
            draw_text(sc, f'x:{int(self.x)}',
                      self.x - self.size, self.y + self.size)
            draw_text(sc, f'y:{int(self.y)}',
                      self.x - self.size, self.y + self.size + 10)
            draw_text(sc, f'angel:{int(self.angle)}',
                      self.x - self.size, self.y + self.size + 20)

            pygame.draw.line(sc, (100, 100, 100), *self.lines_pos[2], 3)
            pygame.draw.line(sc, (50, 50, 50), *self.lines_pos[1], 3)
        self.sprite.draw(sc, self.x, self.y, self.angle)


class ImageClass:
    def __init__(self, filename: str, x: int = 100, y: int = 100, layer: int = 0, scale: float = 1):
        self.img = pygame.image.load(filename)
        if scale != 1:
            width, height = self.img.get_size()
            self.img = pygame.transform.scale(self.img, (int(width * scale), int(height * scale)))
        self.x = x
        self.y = y
        self.layer = layer

    def draw(self, sc, layer: int = 0):
        if self.layer != layer:
            return
        sc.blit(self.img, (self.x, self.y))


class GameClass:
    running = 0
    hand_control = 0
    H = 765
    W = 1360
    game_starting = 10
    images = {
        'earth': ImageClass(filename='img/earth.png', x=900, y=500, scale=1),
        'luna': ImageClass(filename='img/luna.png', x=-20, y=550, scale=.5),
        'sattelite_base': ImageClass(filename='img/sattelite_base.png', x=1130, y=535, scale=1),
        'sattelite_base_user': ImageClass(filename='img/sattelite_base.png', x=150, y=580, scale=.7),
        # 'sokol': ImageClass(filename='img/sokol.png', x=-150, y=535, scale=1),
    }

    sputniks = []

    select_sputnik = 0
    in_range = -1

    def __init__(self, client: WebSocketClient):
        self.client = client
        self.reset()

        # cursor = [MouseCursor, HandCursor][0]()
        self.sc = pygame.display.set_mode((self.W, self.H), pygame.NOFRAME)
        # cursor_img = pygame.image.load('img/cursor2.png')
        pygame.mouse.set_visible(False)
        pygame.font.init()

    def reset(self):
        self.running = 0
        self.hand_control = 0
        self.sputniks = [
            Sputnik(171, 585, angle=50, user_angle=50,
                    filename='sattelite_plate.png', scale=.5,
                    img_params={'width': 129, 'height': 156, 'angle': -90}),
            Sputnik(211, 397, angle=110, user_angle=144),
            Sputnik(257, 194, angle=170, user_angle=25),
            Sputnik(620, 68, angle=200, user_angle=190),
            Sputnik(724, 337, angle=110, user_angle=25),
            Sputnik(1085, 170, angle=205, user_angle=280),
            Sputnik(1161, 543,
                    angle=100, user_angle=143,
                    filename='sattelite_plate.png', scale=1,
                    img_params={'width': 129, 'height': 156, 'angle': -90}),
        ]

        self.sputniks[0].set_active(True)
        self.sputniks[1].set_active(True)

        self.game_starting = 10
        self.in_range = -1

    def active_control(self):
        self.change_sputnik(0)
        self.hand_control = 1

    def stop(self):
        self.running = 0

    def get_signal_line(self, index: int, prev_index: int = None,
                        input_signal: list = None,
                        mode=1,
                        color=(100, 100, 100)):
        # input_signal = [p0, p1]
        # p0 - стартоая точка луча
        # p1 - конечная точка луча (на текущем спутнике)
        sputnik = self.sputniks[index]

        if input_signal is None:
            mode = 0

        if mode == 0:
            a = radians(sputnik.angle)
            dx = sputnik.power * sin(a)
            dy = sputnik.power * cos(a)
            laser = [[sputnik.x, sputnik.y], [sputnik.x + dy, sputnik.y - dx]]

            if prev_index is not None:
                point = cross(sputnik.lines_pos[sputnik.mode], input_signal)
                if not point:
                    point = cross(sputnik.lines_pos[1 - sputnik.mode], input_signal)
                if point:
                    input_signal[1] = point
                else:
                    return None

            return laser

        elif mode == 1:
            p = cross(input_signal, sputnik.lines_pos[sputnik.mode])
            if p:
                input_signal[1] = p
                angle = degrees(atan2((input_signal[1][0] - input_signal[0][0]),
                                      (input_signal[1][1] - input_signal[0][1]))) + 90
                angle = sputnik.angle * 2 - angle

                a = radians(angle)
                return [p, [p[0] + sputnik.power * cos(a), p[1] - sputnik.power * sin(a)]]

    def draw_laser(self, is_user=False):
        color = [(200, 10, 10), (10, 200, 10)][is_user]
        p0 = None

        has_take = False
        prev_index = None
        for index, sputnik in list(enumerate(self.sputniks))[::None if is_user else -1]:
            if has_take:
                break

            input_signal = p0
            p0 = self.get_signal_line(index=index,
                                      prev_index=prev_index,
                                      input_signal=input_signal,
                                      mode=sputnik.mode,
                                      color=color)
            if input_signal:
                pygame.draw.line(self.sc, color, *input_signal, 3)
            p_index = prev_index
            prev_index = index

            if not index:
                continue

            if not p0:
                if is_user and index != self.in_range:
                    self.in_range = index
                    self.client.send('?satellite', f'in_range:{int(index - 1)}')
                break

            if not on_config:
                if sputnik.active != is_user:
                    sputnik.set_active(is_user)
                    has_take = True

            if has_take:
                self.client.send('?satellite', f'take:{index - (1 - is_user)}')
                sputnik.take(is_user, True)
                self.sputniks[2 * index - p_index].take(is_user, False)
                return True

    def change_sputnik(self, i):  # 1 - next, -1 - prev
        self.select_sputnik += i
        if self.select_sputnik < 0:
            for index, sputnik in enumerate(self.sputniks):
                if not sputnik.active:
                    break
                self.select_sputnik = index
        elif self.select_sputnik >= len(self.sputniks):
            self.select_sputnik = 0
        elif not self.sputniks[self.select_sputnik].active:
            self.select_sputnik = 0

        for index, sputnik in enumerate(self.sputniks):
            sputnik.is_hover = index == self.select_sputnik
        self.client.send('?satellite', f'active:{self.select_sputnik}')
        print(self.select_sputnik)

    def rotate_sputnik(self, angle):
        self.sputniks[self.select_sputnik].rotate(angle)

    def game(self):
        self.running = 1
        starfield = Starfield(self.sc)
        tracker = handTracker(sc=self.sc, sc_h=self.H, sc_w=self.W)
        stop_change = False
        active_key = None

        key_test_list = {
            'rotate_left': pygame.K_LEFT,
            'rotate_right': pygame.K_RIGHT,
        }
        if on_config:
            key_test_list.update({
                'move_left': pygame.K_a,
                'move_right': pygame.K_d,
                'move_up': pygame.K_w,
                'move_down': pygame.K_s,
            })
        while self.running:
            if self.game_starting:
                self.game_starting -= 1

                if not self.game_starting:
                    for sputnik in self.sputniks:
                        sputnik.game_run = True

            self.sc.fill((0, 0, 0))
            starfield.draw()

            for img in self.images.values():
                img.draw(self.sc, 0)

            if self.hand_control:
                tracker.update()

            for sputnik in self.sputniks:
                sputnik.update()

            if self.draw_laser():
                if self.sputniks[self.select_sputnik].is_hover:
                    self.change_sputnik(-1)

            if self.hand_control:
                self.draw_laser(True)

            for sputnik in self.sputniks:
                sputnik.draw(self.sc)

            if self.hand_control and tracker.mode is not None:
                if tracker.move == 0:
                    self.rotate_sputnik(.5)
                elif tracker.move == 1:
                    self.rotate_sputnik(-.5)
                elif tracker.move == 2:
                    if not stop_change:
                        self.change_sputnik(1)
                        stop_change = True
                else:
                    stop_change = False

            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    sys.exit()
                if i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_ESCAPE:
                        sys.exit()
                    if i.key == pygame.K_UP:
                        self.change_sputnik(1)
                    if i.key == pygame.K_DOWN:
                        self.change_sputnik(-1)

                    if i.key == pygame.K_SPACE:
                        self.sputniks[3].set_active(True)

                    for code, key in key_test_list.items():
                        if i.key == key:
                            active_key = code
                if i.type == pygame.KEYUP:
                    for code, key in key_test_list.items():
                        if i.key == key and active_key == code:
                            active_key = None

            if active_key == 'rotate_left':
                self.rotate_sputnik(1)
            if active_key == 'rotate_right':
                self.rotate_sputnik(-1)

            if active_key == 'move_left':
                self.sputniks[self.select_sputnik].x -= 5
            if active_key == 'move_right':
                self.sputniks[self.select_sputnik].x += 5
            if active_key == 'move_up':
                self.sputniks[self.select_sputnik].y -= 5
            if active_key == 'move_down':
                self.sputniks[self.select_sputnik].y += 5

            pygame.display.update()

            pygame.time.delay(20)


class MainClass:
    game: GameClass = None
    client: WebSocketClient = None

    def __init__(self):
        message_handlers = {
            "command": self.command,
            # "status": status,
        }
        address = "ws://127.0.0.1:8080"

        self.client = WebSocketClient(address, message_handlers)

    def restart_game(self):
        if self.game:
            self.game.stop()
            sleep(1)
        else:
            self.game = GameClass(self.client)
        self.game.reset()
        Thread(target=self.game.game).start()
    def command(self, message):
        if message == 'restart':
            self.restart_game()

        if message == 'pause':
            self.game and self.game.active_control()

    def run(self):
        self.restart_game()
        self.client.start()


if __name__ == '__main__':
    MainClass().run()
