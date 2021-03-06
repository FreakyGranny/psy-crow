from datetime import datetime, timedelta
from threading import Thread
from time import sleep

import requests

from parser import get_counters


class CounterGetter:
    PATH = "alerts"

    def __init__(self, host, receivers, communicator):
        self.host = host
        self.receivers = receivers
        self.communicator = communicator
        self.counters = {}
        self.last_update = datetime.now() - timedelta(hours=1)
        self.ttl = 60

    def force_update(self):
        self.last_update = datetime.now() - timedelta(hours=1)

    def _get_url(self):
        return "{}/{}?receivers={}".format(self.host, self.PATH, ",".join(self.receivers))

    def update_counters(self):
        if self.last_update + timedelta(seconds=self.ttl) > datetime.now():
            return

        response = requests.get(self._get_url())
        if not response.ok:
            return

        self.counters = get_counters(response.json())
        self.last_update = datetime.now()

    def get_counters(self):
        return self.counters


class UpdateThread(Thread):
    def __init__(self, counter_getter):
        Thread.__init__(self)
        self.counter_getter = counter_getter

    def run(self):
        while True:
            sleep(0.5)
            self.counter_getter.update_counters()
