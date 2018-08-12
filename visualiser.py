import os
import tkinter as tk
import queue

from gui import MainApp
from config import Config
from mqtt import MqttThread, MESSAGE_EVENT


def main():
    config = Config()

    backgrounds = {}
    for item in os.listdir(config.background_dir):
        item_path = os.path.join(config.background_dir, item)
        if os.path.isfile(item_path):
            backgrounds["#{}".format(item.split(".png")[0].upper())] = item_path

    message_queue = queue.Queue()
    root = tk.Tk()
    root.title("Alert visualiser v0.2.0")

    app = MainApp(
        parent=root,
        storage=message_queue,
        backgrounds=backgrounds,
        config=config,
    )

    root.bind(MESSAGE_EVENT, lambda e: app.incoming_popup())
    t = MqttThread(
        config=config.mqtt_connection,
        root=root,
        storage=message_queue,
    )
    t.setDaemon(True)
    t.start()
    root.mainloop()


if __name__ == '__main__':
    main()
