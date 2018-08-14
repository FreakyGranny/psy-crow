import os
import tkinter as tk
import queue

from gui import MainApp
from config import Config
from led import ArduinoThread
from mqtt import MqttThread, MESSAGE_EVENT


def main():
    config = Config()

    backgrounds = {}
    for item in os.listdir(config.background_dir):
        item_path = os.path.join(config.background_dir, item)
        if os.path.isfile(item_path):
            backgrounds["#{}".format(item.split(".png")[0].upper())] = item_path

    message_queue = queue.Queue()
    led_queue = queue.Queue()
    root = tk.Tk()
    root.title("Psy-crow v0.4.0")

    app = MainApp(
        parent=root,
        storage=message_queue,
        backgrounds=backgrounds,
        config=config,
    )

    root.bind(MESSAGE_EVENT, lambda e: app.incoming_popup())
    mqtt_thread = MqttThread(
        config=config.mqtt_connection,
        root=root,
        message_queue=message_queue,
        led_queue=led_queue,
    )
    mqtt_thread.setDaemon(True)
    mqtt_thread.start()
    arduino_thread = ArduinoThread(
        root=root,
        message_queue=message_queue,
        led_queue=led_queue,
    )
    arduino_thread.setDaemon(True)
    arduino_thread.start()

    root.mainloop()


if __name__ == '__main__':
    main()
