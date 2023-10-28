import cv2
import mediapipe as mp
import numpy as np
import pygame
import math


class handTracker():
    height = 240
    width = 320
    move: int = None

    def __init__(self, mode=False, maxHands=1, detectionCon=0.5, modelComplexity=1, trackCon=0.5, sc=None,
                 sc_h=None, sc_w=None):
        self.cap = cv2.VideoCapture(0)
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils

        self.sc = sc
        self.sc_h = sc_h
        self.sc_w = sc_w

    def handsFinder(self, draw=True):
        _, image = self.cap.read()
        imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imageRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(image, handLms, self.mpHands.HAND_CONNECTIONS)
        return image

    def positionFinder(self, image, handNo=0, draw=False):
        lmlist = {}
        if self.results.multi_hand_landmarks:
            Hand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(Hand.landmark):
                h, w, c = image.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist[id] = [cx, cy]
            if draw:
                cv2.circle(image, (cx, cy), 0, (255, 0, 255), cv2.FILLED)

        return lmlist

    def is_line(self, lmList, line, k):
        points = [lmList[p] for p in line if p in lmList]
        if len(points) < len(line):
            return False
        x = [p[0] for p in points]
        y = [p[1] for p in points]

        # Создаем матрицу A для МНК
        A = np.vstack([x, np.ones(len(x))]).T

        # Вычисляем коэффициенты линейной регрессии (a и b)
        a, b = np.linalg.lstsq(A, y, rcond=None)[0]

        # Вычисляем отклонения точек от линии
        residuals = np.array(y) - (a * np.array(x) + b)

        # Вычисляем сумму квадратов отклонений
        sum_of_squares = np.sum(residuals ** 2)

        # растояние между точками 0 и 1
        distance = (x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2

        return (sum_of_squares / distance) < k

    @staticmethod
    def is_middle(lmList, line, point, coordinate, k=0.2):

        if line[0] not in lmList or point not in lmList or line[1] not in lmList:
            return False

        if abs(lmList[line[0]][coordinate] - lmList[line[1]][coordinate]) < abs(
                lmList[line[0]][1 - coordinate] - lmList[line[1]][1 - coordinate]):
            return False
        if not (lmList[line[0]][coordinate] < lmList[point][coordinate] < lmList[line[1]][coordinate]):
            return False

        return True

    def update(self):
        image = self.handsFinder()
        lmList = self.positionFinder(image)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = np.rot90(image)
        image = cv2.resize(image, (self.height, self.width), interpolation=cv2.INTER_AREA)

        self.move = None
        if lmList:
            finger = [
                self.is_middle(lmList, (5, 0), 8, 1),  # указательный
                self.is_middle(lmList, (9, 0), 12, 1),  # средний
                self.is_middle(lmList, (13, 0), 16, 1),  # безымянный
                self.is_middle(lmList, (17, 0), 20, 1),  # мизинец
                self.is_line(lmList, [0, 1, 2, 3], 0.2),  # большой
            ]

            if finger == [1, 1, 1, 1, 1]:
                self.move = lmList[0][0] > lmList[4][0]
            elif finger[:4] == [0, 0, 1, 1]:
                self.move = 2

        image = pygame.surfarray.make_surface(image)
        self.sc.blit(image, ((self.sc_w - self.width) / 2, self.sc_h - self.height))


def main():
    tracker = handTracker()

    while True:

        image = tracker.handsFinder()
        lmList = tracker.positionFinder(image)
        if len(lmList) != 0:
            print(lmList[4])

        cv2.imshow("Video", image)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()
