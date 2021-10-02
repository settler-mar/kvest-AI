# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 16:44:27 2017
@author: sakurai
"""

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

detector = HandDetector(detectionCon=0.8)


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

    def __init__(self, position, cap):  # (170, 350)
        x, y = position
        self.position = position
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
        self.cap = cap
        self.channel = 0

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
            self.camImg_pr = cv2.flip(self.camImg_pr, 1)

            if self.active_hand:
                self.processed_hand()

            self.camImg = self.camImg_pr
            sleep(0.05)

    def processed_hand(self):
        camImg = detector.findHands(self.camImg_pr, draw=False)
        lmList, _ = detector.findPosition(camImg, draw=False)

        isDown = False
        if len(lmList) != 0:
            b = vector_len(lmList[0], lmList[5])
            e = vector_len(lmList[3], lmList[5])
            c2 = e / b
            isDown = c2 < .38

            angle = degrees(atan((lmList[9][0] - lmList[0][0]) / (lmList[9][1] - lmList[0][1])))
            ctrl = 1 if angle < -13 else -1 if angle > 13 else 0

            cv2.addText(camImg, str(int(angle)) + " " + str(ctrl), (10, 50), 'Roboto-Regular.ttf',
                        color=(255, 0, 0, 1) if isDown else (0, 255, 0, 1), pointSize=20)

            for i, point in enumerate(lmList):
                cv2.circle(camImg, point, radius=3, color=(0, 0, 255) if isDown else (0, 255, 255), thickness=2)
                # cv2.addText(self.camImg, str(i), point, 'Roboto-Regular.ttf', color=(0, 255, 0, 1))
        else:
            ctrl = 0

        if ctrl != self.posCtrl:
            if ctrl == 0:
                self.upKey()
            else:
                key = self.keyName(ctrl, isDown)
                print('press', key)
                pyautogui.keyDown(key)
                pyautogui.press(key)

            self.posCtrl = ctrl
            self.isDown = isDown

    def keyName(self, ctrl=None, down=None):
        if ctrl is None:
            ctrl = self.posCtrl
        if down is None:
            down = self.isDown
        i = (1 if ctrl < 0 else 0) + (2 if down else 0)
        return ['left', 'right', 'up', 'down'][i]

    def upKey(self):
        print('up', self.keyName())
        pyautogui.keyUp(self.keyName())

    def render(self, image):
        for p in self.pb:
            p.render(image)
        x, y = self.position
        w = 566
        h = 348
        cv2.rectangle(image, (270 + x, 10 + y), (270 + w + x, 10 + h + y), (0xd6, 0xef, 0x78), 4)
        for j in range(13):
            cv2.rectangle(image, (262 + x + w, 20 + y + j * 26), (245 + x + w, 39 + y + j * 26),
                          (0xd6, 0xef, 0x78), -1)
        if self.success:
            b = 10
            camImg = cv2.resize(self.camImg, (w - 38 - b * 2, h - b * 2 - 16))
            x_offset = 278 + b + x
            y_offset = 18 + b + y
            image[y_offset:y_offset + camImg.shape[0], x_offset:x_offset + camImg.shape[1]] = camImg


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


H = 780
W = 1240

cap = cv2.VideoCapture(0)
# cap.set(3, W)
# cap.set(4, H)
# cv2.VideoCapture("rtsp://192.168.1.2:5554/camera", cv2.CAP_FFMPEG)

cams = [
    Camera((174, 350), [cap]),
    Camera((174, 350 + 380), [cap, cap]),
    Camera((174, 350 + 380 * 2), [cap]),
]

timer = Timer((538, 1620), text="", fontFile='CodenameCoderFree4F-Bold.ttf', fontSize=200, color=(255, 0, 0),
              align=1)
timer.setTime("60:00")


def main():
    screen_id = 0

    # get the size of the screen
    screen = screeninfo.get_monitors()[screen_id]
    width = int(screen.width / 2)
    # image_r = read_transparent_png("timer_bg.png")
    image_r = cv2.imread("timer_bg.png")
    img_h, img_w, _ = image_r.shape
    print(image_r.shape)
    height = int(width * img_h / img_w)
    print(screen, height, width)

    window_name = 'projector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.moveWindow(window_name, screen.x - 1, screen.y - 1)
    cv2.resizeWindow(window_name, width, height)

    # cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    # cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # cams[1].handControl(True)
    circles = Circles((30, 1038))
    txt_wrong = Text((538, 115), text="ОБНАРУЖЕНО\nВТОРЖЕНИЕ", fontFile='Batman_Forever_Alternate_Cyr.ttf',
                     fontSize=100,
                     color=(255, 0, 0), align=1)

    txt = Text((270, 1550), text="Копирование файлов\nна удаленный сервер", fontFile='Bicubik.ttf',
               fontSize=30, color=(255, 255, 255), align=0, line_height=1.5)
    while 1:
        im = Image.open("timer_bg.png")
        draw = ImageDraw.Draw(im)

        for cam in cams:
            cam.renderText(draw)
        txt_wrong.render(draw)
        timer.render(draw)
        txt.render(draw)

        image = cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

        circles.render(image)

        for cam in cams:
            cam.render(image)

        cv2.imshow(window_name, image)
        cv2.waitKey(1)


class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

        path = self.path.strip('/').split('/')

        if path[0] == 'hand':
            if path[1] == '1':
                cams[1].channel = 1
                cams[1].handControl(True)
                print('hand control on')
                requests.get(url='http://127.0.0.1:8080/esp/timer/hand:1')
            if path[1] == '0':
                cams[1].channel = 0
                cams[1].handControl(False)
                print('hand control off')
                requests.get(url='http://127.0.0.1:8080/esp/timer/hand:0')
        if path[0] == 'reset':
            cams[1].channel = 0
            cams[1].handControl(False)
            print('hand control off')
            requests.get(url='http://127.0.0.1:8080/esp/timer/hand:0')

        if path[0] == 'time':
            if path[1] == 'pause':
                timer.pause()
            txt = re.search("[0-9][0-9]:[0-9][0-9]", path[1])
            if txt:
                timer.setTime(txt.string)


def server():
    hostName = "localhost"
    serverPort = 8083

    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))
    threading.Thread(target=webServer.serve_forever).start()


if __name__ == '__main__':
    # import sys
    #
    # if sys.version_info.major == 3:
    #     import tkinter as tk, tkinter.font as tk_font
    # else:
    #     import Tkinter as tk, tkFont as tk_font
    # root = tk.Tk()
    # print(tk_font.families())
    # print(tk_font.names())
    server()
    main()
