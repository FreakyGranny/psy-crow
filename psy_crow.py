import os
import tkinter as tk
import queue

from gui import MainApp
from config import Config
from led import ArduinoThread
from mqtt import MqttThread, MESSAGE_EVENT, UPDATE_EVENT
from am_update import CounterGetter, UpdateThread


class Communicator:
    def __init__(self, led_enabled):
        self.message_queue = queue.Queue()
        if led_enabled:
            self.led_queue = queue.Queue()
        else:
            self.led_queue = None

    def is_message_empty(self):
        return self.message_queue.empty()

    def get_message(self):
        return self.message_queue.get_nowait()

    def put_message(self, data):
        return self.message_queue.put(data)

    def is_led_empty(self):
        if self.led_queue:
            return self.led_queue.empty()

    def get_led_task(self):
        if self.led_queue:
            return self.led_queue.get_nowait()

    def put_led_task(self, task):
        if self.led_queue:
            self.led_queue.put(task)


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

    communicator = Communicator(config.led_enabled)
    root = tk.Tk()
    root.title("Psy-crow v0.11.0")

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
        config=config.mqtt_connection,
        root=root,
        communicator=communicator,
    )
    mqtt_thread.setDaemon(True)
    mqtt_thread.start()

    if config.led_enabled:
        arduino_thread = ArduinoThread(
            communicator=communicator,
        )
        arduino_thread.setDaemon(True)
        arduino_thread.start()

    root.mainloop()


if __name__ == '__main__':
    main()
