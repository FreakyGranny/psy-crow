from datetime import datetime, timedelta

import requests

from parser import get_led_options, get_counters


class CounterGetter:
    PATH = "alerts"

    def __init__(self, host, receivers, led_queue):
        self.host = host
        self.receivers = receivers
        self.led_queue = led_queue
        self.counters = {}
        self.last_update = datetime.now() - timedelta(hours=1)
        self.ttl = 15

    def _get_url(self):
        return "https://{}/{}?receivers={}".format(self.host, self.PATH, ",".join(self.receivers))

    def update_counters(self, force=False):
        if not force:
            if self.last_update + timedelta(seconds=self.ttl) > datetime.now():
                # print("{} counters actual".format(self.last_update))
                return

        # print("update counters")
        response = requests.get(self._get_url())
        if not response.ok:
            return

        content = response.content.decode("utf-8")
        self.counters = get_counters(content)
        self.led_queue.put(get_led_options(content))
        self.last_update = datetime.now()

    def get_counters(self):
        self.update_counters()

        return self.counters
