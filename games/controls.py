import numpy as np
import cv2
import screeninfo
from PIL import ImageFont, Image, ImageDraw
import random
from math import *
from datetime import datetime, timedelta
from cvzone.HandTrackingModule import HandDetector
import pyautogui
import threading
from time import sleep
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import requests
import socket
import mediapipe as mp


# https://stackoverflow.com/questions/69686420/typeerror-create-int-incompatible-function-arguments

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, modelComplexity=1, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.modelComplex = modelComplexity
        self.trackCon = trackCon
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.maxHands, self.modelComplex,
                                        self.detectionCon, self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils  # it gives small dots onhands total 20 landmark points

    def findHands(self, img, draw=True):
        # Send rgb image to hands
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)  # process the frame
        #     print(results.multi_hand_landmarks)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:

                if draw:
                    # Draw dots and connect them
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)

        return img

    def findPosition(self, img, handNo=0, draw=True):
        """Lists the position/type of landmarks
        we give in the list and in the list ww have stored
        type and position of the landmarks.
        List has all the lm position"""

        lmlist = []

        # check wether any landmark was detected
        if self.results.multi_hand_landmarks:
            # Which hand are we talking about
            myHand = self.results.multi_hand_landmarks[handNo]
            # Get id number and landmark information
            for id, lm in enumerate(myHand.landmark):
                # id will give id of landmark in exact index number
                # height width and channel
                h, w, c = img.shape
                # find the position
                cx, cy = int(lm.x * w), int(lm.y * h)  # center
                # print(id,cx,cy)
                lmlist.append([
                    # id,
                    cx, cy])

                # Draw circle for 0th landmark
                if draw:
                    cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)

        return lmlist


detector = handDetector(
    # detectionCon=0.8,
    maxHands=1,
    mode=False,
)


def vector_len(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def read_transparent_png(filename):
    image_4channel = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
    alpha_channel = image_4channel[:, :, 3]
    rgb_channels = image_4channel[:, :, :3]

    # White Background Image
    white_background_image = np.ones_like(rgb_channels, dtype=np.uint8) * 255

    # Alpha factor
    alpha_factor = alpha_channel[:, :, np.newaxis].astype(np.float32) / 255.0
    alpha_factor = np.concatenate((alpha_factor, alpha_factor, alpha_factor), axis=2)

    # Transparent Image Rendered on White Background
    base = rgb_channels.astype(np.float32) * alpha_factor
    white = white_background_image.astype(np.float32) * (1 - alpha_factor)
    final_image = base + white
    return final_image.astype(np.uint8)


class ProgressBar:
    volume: int
    h = 16
    w = 250

    def __init__(self, position, color=(0xd8, 0xeb, 0x82), koef=None, alf=(1, 2, 3, 4),
                 ak=(.1, .2, .3, .4)):
        self.position = position
        self.color = color
        if not koef:
            koef = []
            for i in range(3):
                koef.append(random.randint(0, self.w - sum(koef)))
            koef.append(self.w - sum(koef))
        self.koef = koef
        self.alf = alf or (random.randint(0, 30) / 10 for i in range(4))
        self.ak = ak or (random.random() for i in range(4))

    def update(self):
        x = datetime.now().timestamp()
        self.volume = int(abs(sum([self.koef[i] * sin(x * self.ak[i] + self.alf[i]) for i in range(4)])))

    def draw(self, img):
        cv2.rectangle(img, (self.position[0] - self.w, self.position[1] + self.h), self.position, self.color, 1,
                      cv2.LINE_AA)
        cv2.rectangle(img, (self.position[0] - self.volume, self.position[1] + self.h), self.position, self.color, -1)

    def render(self, img):
        self.update()
        self.draw(img)


class Text:
    def __init__(self, position, len=20, text=None, fontFile: str = "InconsolataHellenic.ttf", fontSize: int = 18,
                 color=(0x78, 0xd6, 0xee), align=2, line_height=1.1):
        self.text = text or ('%06x' % random.randrange(16 ** len)).upper()
        self.need_random = text is None
        self.position = position
        self.font = ImageFont.truetype(fontFile, fontSize)
        self.color = color
        self.align = align
        _, self.dy = ImageDraw.Draw(Image.new('RGB', (1000, 1000))).textsize("text", font=self.font)
        self.dy = int(self.dy * line_height)

    def update_text(self):
        if not self.need_random:
            return
        for j in range(5):
            i = random.randint(0, len(self.text) - 1)
            self.text = self.text[:i] + chr(random.randint(65, 90)) + self.text[i + 1:]

    def drawLine(self, draw, text, pos):
        size = (0, 0)
        if self.align:
            size = draw.textsize(text, font=self.font)
        if self.align == 2:
            pos = (pos[0] - size[0], pos[1])
        if self.align == 1:
            pos = (pos[0] - size[0] / 2, pos[1])
        draw.text(pos, text, font=self.font, fill=self.color)

    def draw(self, draw):
        text = self.text.split("\n")
        if len(text) == 1:
            self.drawLine(draw, text[0], self.position)
        else:
            pos = self.position
            for i, txt in enumerate(text):
                self.drawLine(draw, txt, (pos[0], pos[1] + i * self.dy))

    def render(self, draw):
        self.update_text()
        self.draw(draw)


class Circles:
    def __init__(self, position, count=14, color=(0xd8, 0xeb, 0x82)):
        self.position = position
        self.circles = [random.randint(0, 1) for i in range(count)]
        self.color = color

    def update(self):
        for j in range(5):
            i = random.randint(0, len(self.circles) - 1)
            self.circles[i] = 1 - self.circles[i]

    def draw(self, image):
        for j in range(len(self.circles)):
            cv2.circle(image, (self.position[0], self.position[1] + j * 18), 7, self.color,
                       -1 if self.circles[j] else 1, cv2.LINE_AA)

    def render(self, image):
        self.update()
        self.draw(image)


class Camera:
    success = None
    camImg = None
    camImg_pr = None
    active_hand: bool = False
    posCtrl: int = 0
    isDown: bool = False
    flip: bool = False
    up_ctrl = 0
    hand_is_online: bool = False
    hand_board = False
    only_cam = False
    w = 566
    h = 348

    def __init__(self, position, cap, flip=False):  # (170, 350)
        if not position:
            position = 0, 0
            self.only_cam = True
        else:
            x, y = position
            self.texts = [
                Text(len=random.randint(18, 24), position=(236 + x, 20 + y)),
                Text(len=random.randint(18, 24), position=(236 + x, 40 + y)),
                Text(len=random.randint(18, 24), position=(236 + x, 60 + y)),
                Text(len=random.randint(18, 24), position=(236 + x, 80 + y))
            ]
            self.pb = [
                ProgressBar((236 + x, 120 + y)),
                ProgressBar((236 + x, 142 + y)),
                ProgressBar((236 + x, 162 + y)),
            ]

        self.position = position
        self.cap = cap
        self.cap_type = [isinstance(s, str) for s in cap]
        self.channel = 0
        self.flip = flip

        threading.Thread(target=self.update).start()

    def handControl(self, val: bool):
        self.active_hand = val
        if not val:
            self.upKey()

    def renderText(self, draw):
        for text in self.texts:
            text.render(draw)

    def update(self):
        last_active_channel = self.channel
        while 1:
            if self.cap_type[self.channel]:
                try:
                    res = requests.get(self.cap[self.channel], stream=True, verify=False, timeout=3)
                    resp = res.raw
                    image = np.asarray(bytearray(resp.read()), dtype="uint8")
                    self.camImg_pr = cv2.imdecode(image, cv2.IMREAD_COLOR)
                    self.success = True
                except requests.exceptions.ConnectionError:
                    print('build http connection failed')
                    self.success = False
                except socket.timeout:
                    self.success = False
                    print('download failed')
                except:
                    self.success = False
                    print('Other error')
            else:
                self.success, self.camImg_pr = self.cap[self.channel].read()

            if not self.success:
                print('NOT VIDEO')
                self.channel += 1
                if self.channel >= len(self.cap):
                    self.channel = 0
                if self.channel == last_active_channel:
                    self.camImg = cv2.imread("not_video.jpg")
                    self.success = True
                    sleep(5)
                continue

            last_active_channel = self.channel
            if self.flip:
                self.camImg_pr = cv2.flip(self.camImg_pr, 1)

            if self.active_hand:
                self.processed_hand()

            self.camImg = self.camImg_pr
            sleep(0.05)

    def processed_hand(self):
        camImg = detector.findHands(self.camImg_pr, draw=False)
        lmList = detector.findPosition(camImg, draw=False)

        isDown = False
        if len(lmList) != 0:
            h, w, _ = camImg.shape
            if not self.hand_is_online:
                self.hand_board = [
                    int(min(lmList)[0] * 0.9),
                    int(max(lmList)[0] * 1.1)
                ]
                # print(lmList)
                c = (self.hand_board[0] + self.hand_board[1]) / 2
                self.hand_board = [
                    int(c - w / 7),
                    int(c + w / 7)
                ]
                print('hand board', self.hand_board)
                if abs(w / 2 - c) > w / 3:
                    return

            for x in self.hand_board:
                cv2.line(camImg, (x, 10), (x, h - 10), (0, 0, 255), 2)

            self.hand_is_online = True
            if lmList[9][1] == lmList[0][1]:
                ctrl = self.posCtrl
                isDown = self.isDown
            else:
                b = vector_len(lmList[0], lmList[5])
                e = vector_len(lmList[3], lmList[5])
                c2 = e / b
                isDown = c2 < .35

                hand_pos = [
                    int(min(lmList)[0]),
                    int(max(lmList)[0])
                ]
                ctrl = -1 if self.hand_board[0] > hand_pos[0] else 1 if self.hand_board[1] < hand_pos[1] else 0

                # angle = degrees(atan((lmList[9][0] - lmList[0][0]) / (lmList[9][1] - lmList[0][1])))
                # ctrl = 1 if angle < -13 else -1 if angle > 13 else 0

                # cv2.addText(camImg, str(int(angle)) + " " + str(ctrl), (10, 50), 'Roboto-Regular.ttf',
                #            color=(255, 0, 0, 1) if isDown else (0, 255, 0, 1), pointSize=20)

                for i, point in enumerate(lmList):
                    cv2.circle(camImg, point, radius=3, color=(0, 0, 255) if isDown else (0, 255, 255), thickness=2)
                    # cv2.addText(self.camImg, str(i), point, 'Roboto-Regular.ttf', color=(0, 255, 0, 1))
        else:
            self.hand_is_online = False
            ctrl = 0
            # print(datetime.now().isoformat(), 'lost')

        if ctrl == 0:
            if self.up_ctrl < 3:
                self.up_ctrl += 1
                ctrl = self.posCtrl
        else:
            self.up_ctrl = 0

        if ctrl != self.posCtrl:
            if ctrl == 0:
                # print(datetime.now().isoformat(), 'up')
                self.upKey()
            else:
                # self.upKey()
                key = self.keyName(ctrl, isDown)
                # print(datetime.now().isoformat(), 'press', key)
                pyautogui.keyDown(key)
                # pyautogui.press(key)

            self.posCtrl = ctrl
            self.isDown = isDown

    def keyName(self, ctrl=None, down=None):
        if ctrl is None:
            ctrl = self.posCtrl
        if down is None:
            down = self.isDown
        i = (1 if ctrl < 0 else 0) + (2 if down else 0)
        return ['right', 'left', 'down', 'up'][i]

    def upKey(self):
        # print('up', self.keyName())
        for key in ['right', 'left', 'down', 'up']:
            pyautogui.keyUp(key)

    def render(self, image):
        x, y = self.position
        x_offset, y_offset = self.position
        b = 0
        b_ = [0, 0]
        if not self.only_cam:
            b = 10
            x_offset += 278 + b
            y_offset += 18 + b
            b_ = [38, 16]

            for p in self.pb:
                p.render(image)
            cv2.rectangle(image, (270 + x, 10 + y), (270 + self.w + x, 10 + self.h + y), (0xd6, 0xef, 0x78), 4)
            for j in range(13):
                cv2.rectangle(image, (262 + x + self.w, 20 + y + j * 26), (245 + x + self.w, 39 + y + j * 26),
                              (0xd6, 0xef, 0x78), -1)

        if self.success:
            try:
                camImg = cv2.resize(self.camImg, (self.w - b_[0] - b * 2, self.h - b * 2 - b_[1]))
                image[y_offset:y_offset + camImg.shape[0], x_offset:x_offset + camImg.shape[1]] = camImg
            except:
                pass


class Timer(Text):
    end_time: float = None
    run: bool = False

    def pause(self):
        self.run = False

    def setTime(self, value: str):
        value = value.split(':')
        print('set time', value)
        self.run = True
        self.end_time = (datetime.now() + timedelta(minutes=int(value[0]), seconds=int(value[1]))).timestamp()

    def update_text(self):
        if not self.run:
            return

        if not self.end_time:
            self.text = "00:00:00"
            return

        t = int((self.end_time - datetime.now().timestamp()) * 100)
        if t < 0:
            self.text = "00:00:00"
            return
        # print(t)
        # f = '{:02d}:{:02d}:{:02d}' if int(t / 50) % 2 else '{:02d} {:02d} {:02d}'
        f = '{:02d}:{:02d}:{:02d}'
        self.text = f.format(int(t / 6000), int((t % 6000) / 100), t % 100)
