import time
import sys
import pygame
from CursorClass import HandCursor, MouseCursor
import cv2
import numpy as np
from math import *

H = 780
W = 1240
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


def draw_text(text, x, y, color=(0, 0, 0), size=12, font_name=None, align="nw"):
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


class Sputnik:
    size = 50
    power: int
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

    def draw(self):
        if self.active:
            x, y = cursor.position
            x = int(x * W)
            y = int(y * H)
            if self.is_hover and cursor.isDown:
                hover = 2
                dx = self.click_pos[0] - x - self.click_pos[1] + y
                if dx != 0:
                    d = log(abs(dx)) / 10
                    if d > self.speed:
                        d = self.speed
                    if dx < 0:
                        self.angle -= d
                    else:
                        self.angle += d
                    if self.angle > self.angle_extr[1]:
                        self.angle = self.angle_extr[1]

                    if self.angle < self.angle_extr[0]:
                        self.angle = self.angle_extr[0]
            else:
                hover = abs(x - self.x) < self.size and abs(y - self.y) < self.size
                if hover and self.can_active and (self.is_hover == 0) and cursor.isDown:
                    hover = 2
                    self.click_pos = (x, y)
                    self.is_hover = 1
                else:
                    self.is_hover = 0
                    self.can_active = not cursor.isDown and hover
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
        draw_text(self.angle, self.x - self.size, self.y + self.size)

        a = radians(self.angle)
        dx = self.size * sin(a)
        dy = self.size * cos(a)
        self.line_pos = ([self.x + dx, self.y + dy], [self.x - dx, self.y - dy])
        pygame.draw.line(sc, (0, 0, 0), self.line_pos[0], self.line_pos[1], 3)
        pygame.draw.line(sc, (50, 50, 50), [self.x, self.y], [self.x + dy * 2, self.y - dx * 2], 3)


def draw_cursor():
    if cursor.isDown:
        draw_text('is down', 20, 20, (0, 0, 200))
        for sputnik in sputniks:
            if sputnik.is_hover:
                return
    # rot = pygame.transform.rotate(cursor_img, cursor_alpha)
    # rot_rect = rot.get_rect(center=(32, 32), bottomright=cursor.position)
    # sc.blit(rot, rot_rect)
    x, y = cursor.position

    # cursor_rect = cursor_img.get_rect(bottomright=cursor.position)
    x = int(x * W)
    y = int(y * H)
    pygame.draw.line(sc, (0, 0, 0), [x - 32, y], [x - 12, y], 3)
    pygame.draw.line(sc, (0, 0, 0), [x, y - 30], [x, y - 10], 3)
    pygame.draw.line(sc, (0, 0, 0), [x + 12, y], [x + 32, y], 3)
    pygame.draw.line(sc, (0, 0, 0), [x, y + 12], [x, y + 32], 3)
    pygame.draw.circle(sc, (0, 0, 0), (x, y), 25, 3)

    # sc.blit(cursor_img, cursor_rect)


def cross(x1_1, y1_1, x1_2, y1_2, x2_1, y2_1, x2_2, y2_2):
    A1 = y1_1 - y1_2
    B1 = x1_2 - x1_1
    C1 = x1_1 * y1_2 - x1_2 * y1_1
    A2 = y2_1 - y2_2
    B2 = x2_2 - x2_1
    C2 = x2_1 * y2_2 - x2_2 * y2_1

    if B1 * A2 - B2 * A1 and A1:
        y = (C2 * A1 - C1 * A2) / (B1 * A2 - B2 * A1)
        x = (-C1 - B1 * y) / A1
        if all([x > min(x1_1, x1_2) and x < max(x1_1, x1_2) and y > min(y1_1, y1_2) and y < max(y1_1, y1_2),
                x > min(x2_1, x2_2) and x < max(x2_1, x2_2) and y > min(y2_1, y2_2) and y < max(y2_1, y2_2)]):
            return [x, y]
    elif B1 * A2 - B2 * A1 and A2:
        y = (C2 * A1 - C1 * A2) / (B1 * A2 - B2 * A1)
        x = (-C2 - B2 * y) / A2
        if all([x > min(x1_1, x1_2) and x < max(x1_1, x1_2) and y > min(y1_1, y1_2) and y < max(y1_1, y1_2),
                x > min(x2_1, x2_2) and x < max(x2_1, x2_2) and y > min(y2_1, y2_2) and y < max(y2_1, y2_2)]):
            return [x, y]


def draw_laser(is_user=False):
    color = [(200, 10, 10), (10, 200, 10)][is_user]
    i = 0 if is_user else -1
    a = radians(sputniks[i].angle)
    p0 = [[sputniks[i].x, sputniks[i].y],
          [sputniks[i].x + sputniks[i].power * cos(a), sputniks[i].y - sputniks[i].power * sin(a)]]
    has_take = False
    for sputnik in sputniks[1:None if is_user else -1][::None if is_user else -1]:
        if has_take:
            break
        p = cross(*p0[0], *p0[1], *sputnik.line_pos[0], *sputnik.line_pos[1])
        if p:
            p0[1] = p
            if not on_config:
                if sputnik.active != is_user:
                    sputnik.set_active(is_user)
                    has_take = True
        pygame.draw.line(sc, color, p0[0], p0[1], 3)

        if not p or p0[0][1] == p0[1][1]:
            break
        if has_take:
            continue

        angle = degrees(atan((p0[1][0] - p0[0][0]) / (p0[1][1] - p0[0][1]))) - 90
        if p0[0][1] < p0[1][1]:
            angle += 180
        angle = sputnik.angle * 2 - angle

        a = radians(angle)
        p0 = [p, [p[0] + sputnik.power * cos(a), p[1] - sputnik.power * sin(a)]]
    if has_take:
        sputnik.take()


def draw_cam():
    # рисуем картинку с камеры
    if cursor.camImg is None:
        return
    scale_percent = 20  # percent of original size
    width = int(cursor.camImg.shape[1] * scale_percent / 100)
    height = int(cursor.camImg.shape[0] * scale_percent / 100)
    dim = (width, height)
    cam_image = cv2.resize(cursor.camImg, dim, interpolation=cv2.INTER_AREA)

    cam_image = convert_opencv_img_to_pygame(cam_image)
    sc.blit(cam_image, (W - width, H - height))


cursor = [MouseCursor, HandCursor][1]()
sc = pygame.display.set_mode((W, H), pygame.NOFRAME)
cursor_img = pygame.image.load('cursor2.png')
pygame.mouse.set_visible(False)
pygame.font.init()

sputniks = [
    Sputnik(.65, .75, active=True, angle=140),
    Sputnik(.38, .77, angle=85),
    Sputnik(.14, .51, angle=12),
    Sputnik(.24, .14, angle=307),
    Sputnik(.55, .03, angle=261),
    Sputnik(.79, .24, angle=221),
    Sputnik(.88, .6, angle=111),
]


def main():
    while 1:
        sc.fill((100, 150, 200))  # залить фон
        cursor.update()

        draw_cursor()
        draw_cam()

        for sputnik in sputniks:
            sputnik.draw()
        draw_laser()
        draw_laser(True)

        pygame.display.update()
        for i in pygame.event.get():
            if i.type == pygame.QUIT:
                sys.exit()

        pygame.time.delay(20)


if __name__ == '__main__':
    main()
