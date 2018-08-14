from threading import Thread
from time import sleep

import paho.mqtt.client as mqtt

from parser import get_led_options, get_messages, Message

MESSAGE_EVENT = "<<MessageGenerated>>"


class QClient(mqtt.Client):
    def __init__(self, message_queue, led_queue, root, topic):
        mqtt.Client.__init__(self)
        self.message_queue = message_queue
        self.led_queue = led_queue
        self.root = root
        self.topic = topic


class MqttThread(Thread):
    def __init__(self, config, root, message_queue, led_queue):
        Thread.__init__(self)
        self.config = config
        self.root = root
        self.client = QClient(
            message_queue=message_queue,
            led_queue=led_queue,
            root=self.root,
            topic=self.config["topic"]
        )
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    @staticmethod
    def _on_connect(client, userdata, flags, rc):
        if rc:
            raise Exception("MQTT connected with error")

        client.subscribe(client.topic)

    @staticmethod
    def _on_message(client, userdata, msg):
        client.led_queue.put(get_led_options(msg.payload.decode("utf-8")))

        for message in get_messages(msg.payload.decode("utf-8")):
            client.message_queue.put(message)
            client.root.event_generate(MESSAGE_EVENT)

    def run(self):
        sleep(2)
        try:
            self.client.connect(
                host=self.config["host"],
                port=self.config["port"],
                keepalive=60,
            )
            sleep(1)
            self.client.loop_forever()
        except Exception as e:
            self.client.message_queue.put(
                Message(
                    title="System",
                    text=str(e),
                    color="#707070"
                )
            )
            self.client.root.event_generate(MESSAGE_EVENT)
