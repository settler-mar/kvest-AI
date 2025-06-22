import cv2
import mediapipe as mp
import numpy as np
import pygame
import math


class handTracker():
  height = 240
  width = 320
  move: int = None  # Значение текущего распознанного жеста (ID)

  def __init__(self, mode=False, maxHands=1, detectionCon=0.8, modelComplexity=1, trackCon=0.8, sc=None,
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
    A = np.vstack([x, np.ones(len(x))]).T
    a, b = np.linalg.lstsq(A, y, rcond=None)[0]
    residuals = np.array(y) - (a * np.array(x) + b)
    sum_of_squares = np.sum(residuals ** 2)
    distance = (x[0] - x[1]) ** 2 + (y[0] - y[1]) ** 2
    return (sum_of_squares / distance) < k

  @staticmethod
  def is_middle(lmList, line, point, coordinate=None, k=0.5):
    # Определяет прижат ли палец к ладони, сравнивая расстояние от запястья до основания и до кончика пальца
    if 0 not in lmList or line[0] not in lmList or point not in lmList:
      return False

    wrist = np.array(lmList[0])  # точка запястья
    finger_base = np.array(lmList[line[0]])  # основание пальца
    finger_tip = np.array(lmList[point])  # кончик пальца

    # Расстояние от запястья до основания и до кончика пальца
    dist_base = np.linalg.norm(finger_base - wrist)
    dist_tip = np.linalg.norm(finger_tip - wrist)

    # Если кончик ближе к запястью, чем основание — палец прижат
    return dist_tip < dist_base * (1 + k)

  @staticmethod
  def is_middle__(lmList, line, point, coordinate=None, k=0.35):
    # Определяет прижат ли палец к ладони с учетом положения центра ладони
    if line[0] not in lmList or point not in lmList or 0 not in lmList:
      return False

    # Центр ладони — точка 0 (запястье)
    palm_y = lmList[0][1]  # Y-координата запястья
    tip_y = lmList[point][1]  # Y-координата кончика пальца

    # Если палец находится ближе к запястью, чем центр ладони — он считается прижатым
    # k используется как коэффициент допуска
    return abs(tip_y - palm_y) < k * abs(palm_y)

  @staticmethod
  def is_middle_(lmList, line, point, coordinate, k=0.2):
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
        self.is_line(lmList, [0, 1, 2, 3], 0.1)  # большой
      ]
      print("Finger states:", finger)

      # Распознавание по шаблонам
      if finger == [1, 1, 1, 1, 1]:
        # определение пелец влевого или вправо
        self.move = int(lmList[0][0] > lmList[4][0])
      elif finger[:4] == [0, 0, 1, 1]:
        self.move = 2  # Победа (V)
      elif finger[:2] == [1, 1] and finger[2:] == [0, 0, 0]:
        self.move = 3  # Два пальца
      elif finger == [1, 0, 0, 0, 0]:
        self.move = 4  # Только указательный
      elif finger == [0, 1, 0, 0, 0]:
        self.move = 5  # Только средний
      elif finger == [0, 0, 1, 0, 0]:
        self.move = 6  # Только безымянный
      elif finger == [0, 0, 0, 1, 0]:
        self.move = 7  # Только мизинец
      elif finger == [0, 0, 0, 0, 1]:
        self.move = 8  # Только большой
      elif sum(finger) == 4 and not finger[4]:
        self.move = 9  # Ладонь без большого

      print("Gesture ID:", self.move)

    image = pygame.surfarray.make_surface(image)
    self.sc.blit(image, ((self.sc_w - self.width) / 2, self.sc_h - self.height))


def main():
  tracker = handTracker()
  while True:
    image = tracker.handsFinder()
    lmList = tracker.positionFinder(image)
    if len(lmList) != 0:
      print("Thumb tip:", lmList[4])
    cv2.imshow("Video", image)
    cv2.waitKey(1)


if __name__ == "__main__":
  main()
