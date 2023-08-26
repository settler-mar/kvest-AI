import cv2
from cvzone.HandTrackingModule import HandDetector
import cvzone
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import pygame

H = 780
W = 1240
HK = .8

cap = cv2.VideoCapture(0)
cap.set(3, W)
cap.set(4, H)
detector = HandDetector(detectionCon=0.8)
colorR = (255, 0, 0)

cx, cy, w, h = 100, 100, 200, 200


def vector_len(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


class HandCursor:
    position = (0, 0)
    isDown = False
    lmList = []
    camImg = None

    def update(self, blank_image=None, draw_number=False):
        success, self.camImg = cap.read()
        self.camImg = cv2.flip(self.camImg, 1)
        self.camImg = detector.findHands(self.camImg, draw=False)
        self.lmList, _ = detector.findPosition(self.camImg)

        if len(self.lmList) != 0:
            i = 0
            if blank_image is not None:
                for point in self.lmList:
                    cv2.circle(blank_image, point, radius=3, color=(0, 0, 255), thickness=-1)
                    cv2.addText(blank_image, str(i), point, 'Roboto-Regular.ttf', color=(0, 255, 0, 1))
                    i += 1

            a = vector_len(self.lmList[8], self.lmList[12])
            b = vector_len(self.lmList[0], self.lmList[5])
            d = vector_len(self.lmList[0], self.lmList[8])
            c = a / b

            e = vector_len(self.lmList[3], self.lmList[5])
            c2 = e / b

            # self.isDown = c < .35 and d > b
            self.isDown = c2 < .38
            if blank_image is not None and draw_number:
                cv2.addText(blank_image, '8-12: ' + str(a), (10, 10), 'Roboto-Regular.ttf', color=(255, 0, 0, 1))
                cv2.addText(blank_image, '0-5: ' + str(b), (10, 22), 'Roboto-Regular.ttf', color=(255, 0, 0, 1))
                cv2.addText(blank_image, '8-12/0-5: ' + str(c), (10, 34), 'Roboto-Regular.ttf', color=(255, 0, 0, 1))
                cv2.addText(blank_image, 'isDown: ' + str(self.isDown), (10, 46), 'Roboto-Regular.ttf',
                            color=(255, 0, 0, 1))

                cv2.addText(blank_image, '3-5: ' + str(e), (10, 58), 'Roboto-Regular.ttf', color=(255, 0, 0, 1))
                cv2.addText(blank_image, '3-5/0-5: ' + str(c2), (10, 70), 'Roboto-Regular.ttf', color=(255, 0, 0, 1))
                cv2.addText(blank_image, 'isDown: ' + str(c2 < .38), (10, 82), 'Roboto-Regular.ttf',
                            color=(255, 0, 0, 1))

            x = self.lmList[8][0] / W
            y = self.lmList[8][1] / (H * HK)
            if x > 1: x = 1
            if x < 0: x = 0
            if y > 1: y = 1
            if y < 0: y = 0

            self.position = (x, y)

    def draw_cursor(self, img):
        rows, cols, channels = self.cursor.shape

        a = self.cursor[0:200, 0:200]
        b = img[150:350, 150:350]
        img = cv2.addWeighted(a, 1, b, 0.1, 255)
        # d = cv2.addWeighted(a, 1, b, 0.1, 0)


class MouseCursor(HandCursor):
    def update(self, blank_image=None, draw_number=False):
        coord = pygame.mouse.get_pos()
        x = coord[0] / W
        y = coord[1] / H
        if x > 1: x = 1
        if x < 0: x = 0
        if y > 1: y = 1
        if y < 0: y = 0
        self.isDown = pygame.mouse.get_pressed(3)[0]
        self.position = (x, y)
