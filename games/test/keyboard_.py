
import pyautogui
from time import sleep

sleep(5)
# Holds down the alt key
pyautogui.keyDown("left")
sleep(1)
# Presses the tab key once
pyautogui.press("left")
sleep(1)
# Lets go of the alt key
pyautogui.keyUp("left")
