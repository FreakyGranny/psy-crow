from threading import Thread
from time import sleep

import paho.mqtt.client as mqtt

from parser import get_messages, Message

MESSAGE_EVENT = "<<MessageGenerated>>"
UPDATE_EVENT = "<<UpdateCounters>>"


class QClient(mqtt.Client):
    def __init__(self, config, communicator, root, topic):
        mqtt.Client.__init__(self)
        self.config = config
        self.communicator = communicator
        self.root = root
        self.topic = topic


class MqttThread(Thread):
    def __init__(self, config, root, communicator):
        Thread.__init__(self)
        self.config = config
        self.root = root
        self.client = QClient(
            config=config,
            communicator=communicator,
            root=self.root,
            topic=self.config.mqtt_connection["topic"]
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
        client.root.event_generate(UPDATE_EVENT)
        for message in get_messages(client.config, msg.payload.decode("utf-8")):
            client.communicator.put_message(message)

        client.root.event_generate(MESSAGE_EVENT)

    def run(self):
        sleep(2)
        try:
            self.client.connect(
                host=self.config.mqtt_connection["host"],
                port=self.config.mqtt_connection["port"],
                keepalive=60,
            )
            sleep(1)
            self.client.loop_forever()
        except Exception as e:
            self.client.communicator.put_message(
                Message(
                    title="System",
                    text=str(e),
                    color=self.config.get_color("system")
                )
            )
            self.client.root.event_generate(MESSAGE_EVENT)
