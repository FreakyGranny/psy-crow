# -*- coding: utf-8 -*-

import os

import yaml

CONFIG_FILE_NAME = "config.yml"


class EmptyConfigFileError(Exception):
    pass


class Config:
    FIELD_MQTT_CONNECTION = "mqtt_connection"
    FIELD_BG_DIR = "background_dir"
    FIELD_COUNTERS = "counters"
    FIELD_SHOW_TIME = "show_time"
    FIELD_RECEIVERS = "receivers"
    FIELD_AM_HOST = "am_host"
    FIELD_LED = "led"

    def __init__(self):
        config_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            CONFIG_FILE_NAME
        )
        if not os.path.exists(config_path) or not os.path.isfile(config_path):
            raise FileNotFoundError("{} not found".format(config_path))

        with open(config_path, 'r') as source:
            yaml_content = yaml.safe_load(source.read())
            if not yaml_content:
                raise EmptyConfigFileError()
        self.background_dir = yaml_content.get(self.FIELD_BG_DIR, None)
        self.counters = yaml_content.get(self.FIELD_COUNTERS, [])
        self.mqtt_connection = yaml_content.get(self.FIELD_MQTT_CONNECTION)
        self.show_time = yaml_content.get(self.FIELD_SHOW_TIME)
        self.am_host = yaml_content.get(self.FIELD_AM_HOST)
        self.receivers = yaml_content.get(self.FIELD_RECEIVERS)
        self.led_enabled = yaml_content.get(self.FIELD_LED)
