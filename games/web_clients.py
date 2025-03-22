import chromedriver_autoinstaller

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from screeninfo import get_monitors
import pyautogui
from pynput import keyboard
from common.ws_client import WebSocketClient
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import tkinter as tk
import json

host = '127.0.0.1'


class Display:
  body = None

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

    try:
      service = Service(ChromeDriverManager().install())
      self.driver = webdriver.Chrome(options=options, service=service)
    except:
      print(chromedriver_autoinstaller.get_chrome_version())
      chromedriver_autoinstaller.install()
      self.driver = webdriver.Chrome(options=options)

    self.actions = ActionChains(self.driver)
    self.driver.set_window_position(monitor.x, monitor.y + 50)
    self.driver.set_window_size(monitor.width, monitor.height)
    # self.driver.maximize_window()
    # self.driver.fullscreen_window()
    self.driver.get(page)
    self.reload()

  def reload(self):
    self.driver.fullscreen_window()
    sleep(0.1)
    self.driver.refresh()
    sleep(0.1)
    self.driver.fullscreen_window()
    sleep(3)
    self.body = self.driver.find_element(By.TAG_NAME, 'body')

  def send_key(self, key):
    key_name, key_code, arrow = {
      Keys.UP: ['ArrowUp', 38, Keys.ARROW_UP],
      Keys.DOWN: ['ArrowDown', 40, Keys.ARROW_DOWN],
      Keys.LEFT: ['ArrowLeft', 37, Keys.ARROW_LEFT],
      Keys.RIGHT: ['ArrowRight', 39, Keys.ARROW_RIGHT],
    }[key]
    print('key press', key_name, key_code)
    self.body.send_keys(key)
    self.body.send_keys(arrow)
    js = f"""const event = new KeyboardEvent('keydown', {{
                  key: '{key_name}',
                  code: '{key_name},
                  keyCode: {key_code},
                  which: {key_code},
                  bubbles: true,
                }});
                document.dispatchEvent(event);"""
    # self.driver.execute_script(js)
    self.actions.send_keys(arrow).perform()


class MouseControl:
  pages = [
    [f'http://{host}:8080/snake.html', 2, True],
    [f'http://{host}:8080/video.html', 1],
  ]

  display_windows = None
  mouse_display = -1  # номер экрана на котором мыш. eсли меньше 0, то мышь находится в центре экрана и  эмитирует клавиатуру
  monitors = get_monitors()
  active_screen = None

  x_min, y_min = 100, 100
  x_max, y_max = 500, 500

  def __init__(self):
    self.print_monitor_info()

    # get display setting from http://127.0.0.1:8080/display
    try:
      display_data = requests.get(f"http://{host}:8080/display").json()
    except:
      display_data = {}

    display_data = {data.host: data.display for data in display_data if 'host' in display_data}
    for index, page in enumerate(self.pages):
      if page[0] in display_data:
        self.pages[index][1] = display_data[page[0]]
      else:
        try:
          requests.post(f"http://{host}:8080/display", json={'name': page[0].split('/')[-1],
                                                             'host': page[0],
                                                             'display': page[1]})
        except:
          print('error set display data')
    # print(self.pages)
    # quit()

    self.default_display = self.pages[0][1] if len(self.pages) and self.pages[0][1] < len(self.monitors) else 0
    self.displays = [Display(url,
                             self.monitors[display_number if display_number < len(self.monitors) else 0],
                             *args)
                     for url, display_number, *args in self.pages]
    self.reset()

    message_handlers = {
      "command": self.command,
      "status": self.status,
      "game": self.games_process
    }

    address = f"ws://{host}:8080"

    client = WebSocketClient(address, message_handlers)
    client.start()

    self.client = client

  def show_display_number(self):
    if self.display_windows:
      return
    self.display_windows = []
    for i, monitor in enumerate(self.monitors):
      window = tk.Tk()
      window.overrideredirect(True)  # Remove window decorations
      window.geometry(f"200x100+{monitor.x + monitor.width // 2 - 100}+{monitor.y + monitor.height // 2 - 50}")
      window.wm_attributes("-topmost", True)  # Keep the window on top

      # Create a label for the display number
      label1 = tk.Label(
        window,
        text=f"Display {i}",
        font=("Arial", 20, "bold"),
        bg="black",
        fg="white",
        anchor="center"
      )
      label1.pack(fill=tk.BOTH, expand=True)

      # Create a label for display resolution and position
      label2 = tk.Label(
        window,
        text=f"{monitor.width}x{monitor.height} @ ({monitor.x}, {monitor.y})",
        font=("Arial", 12),
        bg="black",
        fg="white",
        anchor="center"
      )
      label2.pack(fill=tk.BOTH, expand=True)

      self.display_windows.append(window)
      window.after(3000, lambda win=window: win.destroy())  # Auto-close after 3 seconds
      window.update()

    print('show display number')

  def hide_display_number(self):
    if not self.display_windows:
      return

    for window in self.display_windows:
      try:
        window.destroy()
      except tk.TclError:
        pass  # If the window is already destroyed
    self.display_windows = []

  def games_process(self, data):
    data = json.loads(data)
    if data.get('status') == -2:
      self.show_display_number()
    else:
      self.hide_display_number()

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
    if not self.monitors:
      print('monitors not faund')
      return
    print(self.monitors)
    # Перебор дисплеев и получение их свойств
    i = 0
    for monitor in self.monitors:
      i += 1
      print("Дисплей №", i)
      print("Разрешение:", monitor.width, "x", monitor.height)
      print("Смещение по X:", monitor.x)
      print("Смещение по Y:", monitor.y)
      print()

  def set_pos(self, mouse_display=None):
    print('set_pos:', self.mouse_display)
    if mouse_display is not None:
      if self.mouse_display == mouse_display:
        return
      print('set_pos', mouse_display)
      self.mouse_display = mouse_display
    if self.mouse_display < 0:
      self.x_min = self.monitors[0].x + (self.monitors[0].width or 200) / 2
      self.y_min = self.monitors[0].y + (self.monitors[0].height or 200) / 2
      pyautogui.moveTo(self.x_min, self.y_min, duration=0.1)
      return

    self.x_min = self.monitors[self.mouse_display].x + 100
    self.y_min = self.monitors[self.mouse_display].y + 100
    self.x_max = self.monitors[self.mouse_display].x + self.monitors[self.mouse_display].width - 100
    self.y_max = self.monitors[self.mouse_display].y + self.monitors[self.mouse_display].height - 100

    pyautogui.moveTo((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2, duration=0.1)

  def update_mouse_pos(self):
    x, y = pyautogui.position()

    if self.mouse_display < 0:
      dx = x - self.x_min
      dy = y - self.y_min
      if abs(dx) > 1 or abs(dy) > 1:
        if abs(dx) > abs(dy):
          if dx > 0:
            print('>> RIGHT')
            if self.displays:
              self.displays[0].send_key(Keys.RIGHT)
            # pyautogui.keyDown("right")
            # pyautogui.keyUp("right")
          else:
            print('>> LEFT')
            if self.displays:
              self.displays[0].send_key(Keys.LEFT)
            # pyautogui.keyDown('left')
            # pyautogui.keyUp('left')
        else:
          if dy > 0:
            print('>> DOWN')
            if self.displays:
              self.displays[0].send_key(Keys.DOWN)
            # pyautogui.keyDown('down')
            # pyautogui.keyUp('down')
          else:
            print('>> UP')
            if self.displays:
              self.displays[0].send_key(Keys.UP)
            # pyautogui.keyDown('up')
            # pyautogui.keyUp('up')
        print(dx, dy, self.x_min, self.y_min)
        sleep(1)
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

    if key == keyboard.Key.space:
      mouse_control.set_pos(-1)

  listener = keyboard.Listener(on_press=on_key_press)
  listener.start()
  print('run keyboard monitor')

  mouse_control = MouseControl()
  while listener.is_alive():
    mouse_control.processed()
  mouse_control.stop()


if __name__ == '__main__':
  print(chromedriver_autoinstaller.get_chrome_version())
  chromedriver_autoinstaller.install()

  pyautogui.FAILSAFE = False
  main()
