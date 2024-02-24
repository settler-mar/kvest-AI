from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep
from screeninfo import get_monitors
import pyautogui
from pynput import keyboard
from common.ws_client import WebSocketClient
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

pages = [
  ('http://127.0.0.1:8080/snake.html', 2, True),
  ('http://127.0.0.1:8080/video.html', 1),
]


class Display:
  def __init__(self, page, monitor, is_kiosk: bool = False):
    options = Options()
    options.add_experimental_option("excludeSwitches", ['enable-automation'])
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-web-security")
    options.add_argument("--ignore-certificate-errors")
    if is_kiosk:
      options.add_argument("--kiosk")
    options.add_argument("--disable-password-manager-reauthentication")

    service = Service(ChromeDriverManager().install())
    self.driver = webdriver.Chrome(options=options, service=service)
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

  def send_key(self, key):
    print('key press',key)
    self.driver.find_elements(By.TAG_NAME, "body")[0].send_keys(key)


class MouseControl:
  mouse_display = -1  # номер экрана на котором мыш. eсли меньше 0, то мышь находится в центре экрана и  эмитирует клавиатуру
  monitors = get_monitors()
  active_screen = None

  x_min, y_min = 100, 100
  x_max, y_max = 500, 500

  def __init__(self):
    self.print_monitor_info()
    self.default_display = pages[0][1] if pages[0][1] < len(self.monitors) else 0
    self.displays = [Display(url,
                             self.monitors[display_number if display_number < len(self.monitors) else 0],
                             *args)
                     for url, display_number, *args in pages]
    self.reset()

    message_handlers = {
      "command": self.command,
      "status": self.status,
    }

    address = "ws://127.0.0.1:8080"

    client = WebSocketClient(address, message_handlers)
    client.start()

    self.client = client

  def status(self, data):
    status = json.loads(data)
    if "snake" in status and "pass_ok" in status["snake"]:
      if self.active_screen != status["snake"]["screen"]:
        self.active_screen = status["snake"]["screen"]
        self.set_pos(-1 if self.active_screen in ['video', 'game'] else self.default_display)

  def reset(self):
    self.set_pos(self.default_display)

    [display.reload() for display in self.displays]

  def print_monitor_info(self):
    # Перебор дисплеев и получение их свойств
    for i, monitor in enumerate(self.monitors, 1):
      print("Дисплей №", i)
      print("Разрешение:", monitor.width, "x", monitor.height)
      print("Смещение по X:", monitor.x)
      print("Смещение по Y:", monitor.y)
      print()

  def set_pos(self, mouse_display=None):
    if mouse_display is not None:
      if self.mouse_display == mouse_display:
        return
      print('set_pos', mouse_display)
      self.mouse_display = mouse_display
    if self.mouse_display < 0:
      self.x_min = self.monitors[pages[0][1]].x + (self.monitors[pages[0][1]].width or 200) / 2
      self.y_min = self.monitors[pages[0][1]].y + (self.monitors[pages[0][1]].height or 200) / 2
      pyautogui.moveTo(self.x_min, self.y_min, duration=0.1)
      return

    self.x_min = self.monitors[self.mouse_display].x
    self.y_min = self.monitors[self.mouse_display].y
    self.x_max = self.monitors[self.mouse_display].x + self.monitors[self.mouse_display].width
    self.y_max = self.monitors[self.mouse_display].y + self.monitors[self.mouse_display].height

    pyautogui.moveTo((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2, duration=0.1)

  def update_mouse_pos(self):
    x, y = pyautogui.position()

    if self.mouse_display < 0:
      dx = x - self.x_min
      dy = y - self.y_min
      if abs(dx) > 1 or abs(dy) > 1:
        if abs(dx) > abs(dy):
          if dx > 0:
            self.displays[0].send_key(Keys.RIGHT)
            # pyautogui.keyDown("right")
            # pyautogui.keyUp("right")
          else:
            self.displays[0].send_key(Keys.LEFT)
            # pyautogui.keyDown('left')
            # pyautogui.keyUp('left')
        else:
          if dy > 0:
            self.displays[0].send_key(Keys.DOWN)
            # pyautogui.keyDown('down')
            # pyautogui.keyUp('down')
          else:
            self.displays[0].send_key(Keys.UP)
            # pyautogui.keyDown('up')
            # pyautogui.keyUp('up')
        print(dx, dy, self.x_min, self.y_min)
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
    pyautogui.moveTo(x, y, duration=0)

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
  pyautogui.FAILSAFE = False
  main()
