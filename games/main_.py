import sys
import pygame
from typing import List, Tuple
# from common.CursorClass import HandCursor, MouseCursor
import cv2
from math import *
from pygame import gfxdraw
import random
from time import time

on_config = False


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


class Starfield:
    count = 2000

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
                1 / random.randrange(10, 20),  # speed
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

    def __init__(self, filename, width, height, frames_count, frame_start, origin_x, origin_y, frames_per_row,
                 frames_per_col, current_frame=0, fps=25):
        self.frames_count = frames_count  # количество кадров в анимации
        self.current_frame = current_frame  # текущий кадр
        self.frame_start = frame_start  # начальный кадр анимации (например, если анимация начинается с 5 кадра)
        self.image = pygame.image.load(filename)
        self.width = width  # размеры кадра
        self.height = height  # размеры кадра
        self.origin_x = origin_x  # точка отсчета для поворота
        self.origin_y = origin_y  # точка отсчета для поворота
        self.angle = 0
        self.frames_per_row = frames_per_row
        self.frames_per_col = frames_per_col

        self.fps = fps
        self.last_frame_time = 0

    def draw(self, screen, x, y, angle):
        frame_x = ((self.current_frame + self.frame_start) % self.frames_per_row) * self.width
        frame_y = ((self.current_frame + self.frame_start) // self.frames_per_row) * self.height

        frame_rect = pygame.Rect(frame_x, frame_y, self.width, self.height)

        image = self.image.subsurface(frame_rect)

        # поворачиваем изображение
        rotated_img = pygame.transform.rotate(image, angle)

        # определяем прямоугольник отрисовки
        w, h = rotated_img.get_size()
        draw_x = x - w / 2 + self.origin_x
        draw_y = y - h / 2 + self.origin_y

        # отрисовываем
        screen.blit(rotated_img, (draw_x, draw_y))

        pygame.draw.line(screen, (255, 255, 0), [draw_x, draw_y], [draw_x + w, draw_y + h], 2)
        pygame.draw.line(screen, (255, 255, 0), [draw_x, draw_y + h], [draw_x + w, draw_y], 2)

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
    speed = 3
    line_pos = ([0, 0], [0, 0])
    click_pos = (0, 0)

    can_active = 0

    def __init__(self, x, y, power=420, angle=90, active=False):
        self.x = x * 1240
        self.y = y * 780
        self.power = power
        self.active = active or on_config
        self.angle = angle
        self.angle_def = angle
        self.angle_extr = (angle - 60, angle + 60)

    def set_active(self, st):
        self.active = st

    def take(self):
        self.angle = self.angle_extr[0]

    def rotate(self, d):
        self.angle += d
        if self.angle > self.angle_extr[1]:
            self.angle = self.angle_extr[1]
        if self.angle < self.angle_extr[0]:
            self.angle = self.angle_extr[0]

    def draw(self, sc):
        if self.active:
            hover = self.is_hover
        else:
            hover = 3
            if self.angle != self.angle_def:
                self.angle += self.speed / 8
                if self.angle > self.angle_def:
                    self.angle = self.angle_def

        color = [(50, 150, 100), (0, 200, 150), (50, 255, 50), (150, 0, 0)][hover]
        pygame.draw.polygon(sc, color,
                            [[self.x - self.size, self.y - self.size], [self.x - self.size, self.y + self.size],
                             [self.x + self.size, self.y + self.size], [self.x + self.size, self.y - self.size]],
                            width=5)
        draw_text(sc, self.angle, self.x - self.size, self.y + self.size)

        a = radians(self.angle)
        dx = self.size * sin(a)
        dy = self.size * cos(a)
        self.line_pos = ([self.x + dx, self.y + dy], [self.x - dx, self.y - dy])
        pygame.draw.line(sc, (100, 100, 100), self.line_pos[0], self.line_pos[1], 3)
        pygame.draw.line(sc, (50, 50, 50), [self.x, self.y], [self.x + dy * 2, self.y - dx * 2], 3)


class GameClass:
    H = 780
    W = 1240
    sputniks = [
        Sputnik(.65, .75, angle=140),
        Sputnik(.38, .77, angle=63),
        Sputnik(.14, .51, angle=5),
        Sputnik(.24, .14, angle=307),
        Sputnik(.55, .03, angle=261),
        Sputnik(.79, .24, angle=221),
        Sputnik(.88, .6, angle=111),
    ]
    select_sputnik = 0

    def __init__(self):
        self.sputniks[0].active = True
        self.change_sputnik(0)

        # cursor = [MouseCursor, HandCursor][0]()
        self.sc = pygame.display.set_mode((self.W, self.H), pygame.NOFRAME)
        # cursor_img = pygame.image.load('img/cursor2.png')
        pygame.mouse.set_visible(False)
        pygame.font.init()

    def draw_laser(self, is_user=False):
        color = [(200, 10, 10), (10, 200, 10)][is_user]
        i = 0 if is_user else -1
        a = radians(self.sputniks[i].angle)
        p0 = [[self.sputniks[i].x, self.sputniks[i].y],
              [self.sputniks[i].x + self.sputniks[i].power * cos(a),
               self.sputniks[i].y - self.sputniks[i].power * sin(a)]]
        has_take = False
        for sputnik in self.sputniks[1:None if is_user else -1][::None if is_user else -1]:
            if has_take:
                break
            p = cross(p0, sputnik.line_pos)
            if p:
                p0[1] = p
                if not on_config:
                    if sputnik.active != is_user:
                        sputnik.set_active(is_user)
                        has_take = True
            pygame.draw.line(self.sc, color, p0[0], p0[1], 3)

            if not p:
                break
            if has_take:
                continue

            angle = degrees(atan2((p0[1][0] - p0[0][0]), (p0[1][1] - p0[0][1]))) + 90
            angle = sputnik.angle * 2 - angle

            a = radians(angle)
            p0 = [p, [p[0] + sputnik.power * cos(a), p[1] - sputnik.power * sin(a)]]
        if has_take:
            sputnik.take()
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
        print(self.select_sputnik)

    def rotate_sputnik(self, angle):
        self.sputniks[self.select_sputnik].rotate(angle)

    def game(self):
        starfield = Starfield(self.sc)
        sprite = SpriteAnimation("img/sprite_sat4.png", width=850/4, height=630/4, origin_x=200, origin_y=320,
                                 frames_count=6, frame_start=0, frames_per_col=2, frames_per_row=4)
        sprite.current_frame = 3
        while 1:
            self.sc.fill((0, 0, 0))
            starfield.draw()

            sprite.update()
            sprite.draw(self.sc,
                        # self.sputniks[0].x,
                        # self.sputniks[0].y,
                        100, 100,
                        self.sputniks[0].angle)
            pygame.draw.line(self.sc, (100, 0, 0), [95, 95], [105, 105], 2)
            pygame.draw.line(self.sc, (100, 0, 0), [95, 105], [105, 95], 2)

            # cursor.update()

            # draw_cursor()
            # draw_cam()

            for sputnik in self.sputniks:
                sputnik.draw(self.sc)
            if self.draw_laser():
                if self.sputniks[self.select_sputnik].is_hover:
                    self.change_sputnik(-1)
            self.draw_laser(True)

            pygame.display.update()
            for i in pygame.event.get():
                if i.type == pygame.QUIT:
                    sys.exit()
                if i.type == pygame.KEYDOWN:
                    if i.key == pygame.K_ESCAPE:
                        sys.exit()
                    if i.key == pygame.K_LEFT:
                        self.change_sputnik(-1)
                    if i.key == pygame.K_RIGHT:
                        self.change_sputnik(1)
                    if i.key == pygame.K_UP:
                        self.rotate_sputnik(1)
                    if i.key == pygame.K_DOWN:
                        self.rotate_sputnik(-1)

            pygame.time.delay(20)


def main():
    GameClass().game()


if __name__ == '__main__':
    main()
