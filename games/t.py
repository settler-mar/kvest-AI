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

key = 'left'
sleep(2)
print(1)
pyautogui.keyDown(key)
sleep(2)
print(2)
#pyautogui.press(key)
sleep(2)
print(3)
pyautogui.keyUp(key)