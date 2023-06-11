from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from screeninfo import get_monitors
import pyautogui
from pynput import keyboard

pages = [
    # ('http://127.0.0.1:8080/video.html', 0),
    ('http://127.0.0.1:8080/snake.html', 1)
]

mouse_display = 0  # номер экрана на котором мыш. усли -1 то эмитирует клавиатуру

# Получение списка дисплеев
monitors = get_monitors()


def print_monitor_info():
    # Перебор дисплеев и получение их свойств
    for i, monitor in enumerate(monitors, 1):
        print("Дисплей №", i)
        print("Разрешение:", monitor.width, "x", monitor.height)
        print("Смещение по X:", monitor.x)
        print("Смещение по Y:", monitor.y)
        print()


print_monitor_info()


class Display:
    def __init__(self, page, display_number):
        monitor = monitors[display_number if display_number < len(monitors) else 0]
        options = Options()
        options.add_experimental_option("excludeSwitches", ['enable-automation'])
        self.driver = webdriver.Chrome(options=options)
        self.driver.set_window_position(monitor.x, monitor.y + 50)
        self.driver.set_window_size(monitor.width, monitor.height)
        # self.driver.maximize_window()
        self.driver.fullscreen_window()
        self.driver.get(page)
        self.reload()

    def reload(self):
        self.driver.fullscreen_window()
        self.driver.refresh()
        self.driver.fullscreen_window()


displays = [Display(url, display_number) for url, display_number in pages]

x_min, y_min = 100, 100
x_max, y_max = 500, 500


def set_pos():
    global x_min, y_min, x_max, y_max
    if mouse_display == -1:
        x_min = monitors[0].x + monitors[0].width / 2
        y_min = monitors[0].y + monitors[0].height / 2
        pyautogui.moveTo(x_min, y_min, duration=0.1)
        return
    x_min = monitors[0].x
    y_min = monitors[0].y
    x_max = monitors[0].x + monitors[0].width
    y_max = monitors[0].y + monitors[0].height

    pyautogui.moveTo((x_min + x_max) / 2, (y_min + y_max) / 2, duration=0.1)


set_pos()


def on_key_press(key):
    if key == keyboard.Key.esc:
        print("Клавиша Esc нажата. Программа завершена.")
        return False  # Останавливаем прослушивание клавиш


listener = keyboard.Listener(on_press=on_key_press)
listener.start()

while listener.is_alive():
    x, y = pyautogui.position()

    if mouse_display == -1:
        dx = x - x_min
        dy = y - y_min
        if abs(dx) > 2 or abs(dy) > 2:
            if abs(dx) > abs(dy):
                if dx > 0:
                    # pyautogui.press("left")
                    pyautogui.keyDown("right")
                    pyautogui.keyUp("right")
                else:
                    pyautogui.keyDown('left')
                    pyautogui.keyUp('left')
            else:
                if dy > 0:
                    pyautogui.keyDown('down')
                    pyautogui.keyUp('down')
                else:
                    pyautogui.keyDown('up')
                    pyautogui.keyUp('up')
            print(dx, dy)
        pyautogui.moveTo(x_min, y_min, duration=0.1)
        continue

    # Проверяем и ограничиваем координаты курсора
    if x < x_min:
        x = x_min
    elif x > x_max:
        x = x_max
    if y < y_min:
        y = y_min
    elif y > y_max:
        y = y_max

    # Перемещаем курсор в ограниченные координаты
    pyautogui.moveTo(x, y, duration=0.1)
