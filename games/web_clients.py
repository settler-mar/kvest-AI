from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from screeninfo import get_monitors
import pyautogui
from pynput import keyboard
from ws_client import WebSocketClient

pages = [
    ('http://127.0.0.1:8080/snake.html', 2),
    # ('http://127.0.0.1:8080/video.html', 2),
]


class Display:
    def __init__(self, page, monitor):
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
        sleep(0.1)
        self.driver.refresh()
        sleep(0.1)
        self.driver.fullscreen_window()


class MouseControl:
    mouse_display = 0  # номер экрана на котором мыш. усли -1 то эмитирует клавиатуру
    monitors = get_monitors()

    x_min, y_min = 100, 100
    x_max, y_max = 500, 500

    def __init__(self):
        self.print_monitor_info()
        self.displays = [Display(url,
                                 self.monitors[display_number if display_number < len(self.monitors) else 0])
                         for url, display_number in pages]
        self.reset()

        message_handlers = {
            "command": self.command,
            # "game": print,
        }

        address = "ws://127.0.0.1:8080"

        client = WebSocketClient(address, message_handlers)
        client.start()

        self.client = client

    def reset(self):
        if self.displays:
            self.mouse_display = pages[0][1] if pages[0][1] < len(self.monitors) else 0
        self.set_pos()

        [display.reload() for display in self.displays]

    def print_monitor_info(self):
        # Перебор дисплеев и получение их свойств
        for i, monitor in enumerate(self.monitors, 1):
            print("Дисплей №", i)
            print("Разрешение:", monitor.width, "x", monitor.height)
            print("Смещение по X:", monitor.x)
            print("Смещение по Y:", monitor.y)
            print()

    def set_pos(self):
        if self.mouse_display == -1:
            x_min = self.monitors[0].x + self.monitors[0].width / 2
            y_min = self.monitors[0].y + self.monitors[0].height / 2
            pyautogui.moveTo(x_min, y_min, duration=0.1)
            return
        self.x_min = self.monitors[self.mouse_display].x
        self.y_min = self.monitors[self.mouse_display].y
        self.x_max = self.monitors[self.mouse_display].x + self.monitors[self.mouse_display].width
        self.y_max = self.monitors[self.mouse_display].y + self.monitors[self.mouse_display].height

        pyautogui.moveTo((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2, duration=0.1)

    def update_mouse_pos(self):
        x, y = pyautogui.position()

        if self.mouse_display == -1:
            dx = x - self.x_min
            dy = y - self.y_min
            if abs(dx) > 1 or abs(dy) > 1:
                if abs(dx) > abs(dy):
                    if dx > 0:
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
            pyautogui.moveTo(self.x_min, self.y_min, duration=0.1)
            return

        # Проверяем и ограничиваем координаты курсора
        if x < self.x_min:
            x = self.x_min
        elif x > self.x_max:
            x = self.x_max
        if y < self.y_min:
            y = self.y_min
        elif y > self.y_max:
            y = self.y_max

        # Перемещаем курсор в ограниченные координаты
        pyautogui.moveTo(x, y, duration=0.1)

    def command(self, data):
        if data == 'reset':
            self.reset()

    def stop(self):
        self.client.stop()
        [display.driver.close() for display in self.displays]

    def processed(self):
        self.update_mouse_pos()


def main():
    def on_key_press(key):
        if key == keyboard.Key.esc:
            print("Клавиша Esc нажата. Программа завершена.")
            return False  # Останавливаем прослушивание клавиш

    listener = keyboard.Listener(on_press=on_key_press)
    listener.start()

    mouse_control = MouseControl()

    while listener.is_alive():
        mouse_control.processed()
    mouse_control.stop()


if __name__ == '__main__':
    main()
