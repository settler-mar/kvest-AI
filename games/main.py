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
from controls import *


def init_cam(c):
    if len(c) < 3:
        return cv2.VideoCapture(int(c))
    # url = f"http://{c}/Streaming/Channels/102/picture?snapShotImageType=JPEG"
    # return url
    url = f"rtsp://{c}/Streaming/Channels/102"
    return cv2.VideoCapture(url, cv2.CAP_FFMPEG)
    # cap = cv2.VideoCapture(0)
    # cap.set(3, W)
    # cam = cv2.VideoCapture("rtsp://admin:59Intelligence59@192.168.1.23:554/Streaming/Channels/102", cv2.CAP_FFMPEG)
    # cap.set(4, H)


f = open("cams.txt", "r")
cams = []
i = 0
for conf in f.read().split("\n"):
    cams.append(Camera((174, 350 + 380 * i), [init_cam(c) for c in conf.split(" ")], i % 2))
    i = i + 1

H = 780
W = 1240

timer = Timer((538, 1620), text="", fontFile='CodenameCoderFree4F-Bold.ttf', fontSize=200, color=(255, 0, 0),
              align=1)
timer.setTime("60:00")
txt_wrong = Text((538, 115), text="ОБНАРУЖЕНО\nВТОРЖЕНИЕ", fontFile='Batman_Forever_Alternate_Cyr.ttf',
                 fontSize=100,
                 color=(255, 0, 0), align=1)

txt_msg = Text((270, 1550), text="Копирование файлов\nна удаленный сервер", fontFile='Bicubik.ttf',
               fontSize=30, color=(255, 255, 255), align=0, line_height=1.5)

cams[1].channel = 1
cams[1].handControl(True)


def main():
    screen_id = 4
    screen_cnt = len(screeninfo.get_monitors())

    screen = screeninfo.get_monitors()[min(screen_cnt - 1, screen_id)]
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
    while 1:
        im = Image.open("timer_bg.png")
        draw = ImageDraw.Draw(im)

        for cam in cams:
            cam.renderText(draw)
        txt_wrong.render(draw)
        timer.render(draw)
        txt_msg.render(draw)

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

        if path[0] == 'lang':
            tr = {
                'ru': [
                    'ОБНАРУЖЕНО\nВТОРЖЕНИЕ',
                    'Копирование файлов\nна удаленный сервер'
                ], 'ua': [
                    'ВИЯВЛЕНО\nВТОРГНЕННЯ',
                    'Копіювання файлів\nна віддалений сервер'
                ], 'en': [
                    'DETECTED\nINVASION',
                    'Copying files\nfor remote server'
                ],
            }.get(path[1])
            if not tr:
                return

            txt_wrong.text = tr[0]
            txt_msg.text = tr[1]


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
