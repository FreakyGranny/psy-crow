import os
import tkinter as tk
import queue

from gui import MainApp
from config import Config
from led import ArduinoThread
from mqtt import MqttThread, MESSAGE_EVENT, UPDATE_EVENT
from am_update import CounterGetter


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
    root.title("Psy-crow v0.5.0")

    counter_updater = CounterGetter(
        host=config.am_host,
        receivers=config.receivers,
        led_queue=led_queue,
    )

    app = MainApp(
        parent=root,
        storage=message_queue,
        backgrounds=backgrounds,
        config=config,
        counter_updater=counter_updater,
    )

    root.bind(MESSAGE_EVENT, lambda e: app.check_queue())
    root.bind(UPDATE_EVENT, lambda e: app.force_update())
    mqtt_thread = MqttThread(
        config=config.mqtt_connection,
        root=root,
        message_queue=message_queue,
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
