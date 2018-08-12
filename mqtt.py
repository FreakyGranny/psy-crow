from threading import Thread
from time import sleep

import paho.mqtt.client as mqtt

from parser import get_led_options, get_messages, Message

MESSAGE_EVENT = "<<MessageGenerated>>"


class QClient(mqtt.Client):
    def __init__(self, storage, root, topic):
        mqtt.Client.__init__(self)
        self.storage = storage
        self.root = root
        self.topic = topic


class MqttThread(Thread):
    def __init__(self, config, root, storage):
        Thread.__init__(self)
        self.config = config
        self.root = root
        self.storage = storage
        self.client = QClient(
            storage=self.storage,
            root=self.root,
            topic=self.config["topic"]
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc:
            message = "MQTT connected with error"
        else:
            message = "MQTT connected successfully"
        client.storage.put(
            Message(
                title="System",
                text=message,
                color="#707070"
            )
        )
        client.root.event_generate(MESSAGE_EVENT)
        client.subscribe(client.topic)

    @staticmethod
    def _on_message(client, userdata, msg):
        led_options = get_led_options(msg.payload.decode("utf-8"))
        messages = get_messages(msg.payload.decode("utf-8"))
        for message in messages:
            client.storage.put(message)
            client.root.event_generate(MESSAGE_EVENT)

    def run(self):
        self.client.connect(
            host=self.config["host"],
            port=self.config["port"],
            keepalive=60,
        )
        sleep(1)
        self.client.loop_forever()
