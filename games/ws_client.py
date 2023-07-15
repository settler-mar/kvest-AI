import asyncio
import threading
import websocket
from websockets.exceptions import ConnectionClosed
from typing import Dict, Callable, Optional
from time import sleep


class WebSocketClient:
    msg_example = []
    thread = None
    run = True

    def __init__(self, address: str, message_handlers: Optional[Dict[str, Callable[[str], None]]] = None):
        self.address = address
        self.websocket = websocket.WebSocket()
        self.message_handlers = message_handlers or {}

    def connect(self):
        while True:
            try:
                self.websocket.connect(self.address)
                print(f"Connected to {self.address}")
                break
            except (ConnectionRefusedError, TimeoutError):
                print(f"Connection to {self.address} failed. Retrying...")
                sleep(5)

    def receive_messages(self):
        try:
            while self.run:
                message = self.websocket.recv()
                self.handle_message(message)
        except ConnectionClosed:
            print("Connection closed unexpectedly. Reconnecting...")
            self.connect()
            self.receive_messages()

    def handle_message(self, message):
        if ":" in message:
            key, data = message.split(":", 1)
            if key in self.message_handlers:
                callback = self.message_handlers[key]
                callback(data)
            else:
                if key not in self.msg_example:
                    print(f"Skip key: {key}", data)
                    self.msg_example.append(key)
        else:
            print(f"Received invalid message: {message}")

    def send(self, key, data):
        message = f"{key}:{data}"
        self.websocket.send(message)

    def start(self):
        self.connect()
        # Create a thread object
        self.thread = threading.Thread(target=self.receive_messages)

        # Start the thread
        self.thread.start()

    def stop(self):
        self.run = False


if __name__ == "__main__":
    def handle_data(data):
        print(f"Received data: {data}")


    message_handlers = {
        "command": handle_data,
        # "game": handle_data,
        # Add more key-callback pairs as needed
    }

    address = "ws://127.0.0.1:8080"

    client = WebSocketClient(address, message_handlers)
    asyncio.run(client.start())
