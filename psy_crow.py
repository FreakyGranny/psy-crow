import os
import tkinter as tk
import queue

from gui import MainApp
from config import Config
from mqtt import MqttThread, MESSAGE_EVENT, UPDATE_EVENT
from am_update import CounterGetter, UpdateThread


class Communicator:
    def __init__(self):
        self.message_queue = queue.Queue()

    def is_message_empty(self):
        return self.message_queue.empty()

    def get_message(self):
        return self.message_queue.get_nowait()

    def put_message(self, data):
        return self.message_queue.put(data)


def main():
    config = Config()

    backgrounds = {}
    backgrounds_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)),
        config.background_dir
    )
    for item in os.listdir(backgrounds_path):
        item_path = os.path.join(backgrounds_path, item)
        if os.path.isfile(item_path):
            backgrounds["#{}".format(item.split(".png")[0].upper())] = item_path

    communicator = Communicator()
    root = tk.Tk()
    root.title("Psy-crow v0.12.0")

    counter_updater = CounterGetter(
        host=config.am_host,
        receivers=config.receivers,
        communicator=communicator,
    )

    app = MainApp(
        parent=root,
        communicator=communicator,
        backgrounds=backgrounds,
        config=config,
        counter_updater=counter_updater,
    )

    root.bind(MESSAGE_EVENT, lambda e: app.check_queue())
    root.bind(UPDATE_EVENT, lambda e: app.force_update())
    update_thread = UpdateThread(
        counter_getter=counter_updater
    )
    update_thread.setDaemon(True)
    update_thread.start()
    mqtt_thread = MqttThread(
        config=config,
        root=root,
        communicator=communicator,
    )
    mqtt_thread.setDaemon(True)
    mqtt_thread.start()

    root.mainloop()


if __name__ == '__main__':
    main()
