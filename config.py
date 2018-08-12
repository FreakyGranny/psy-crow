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

    def __init__(self):
        if not os.path.exists(CONFIG_FILE_NAME) or not os.path.isfile(CONFIG_FILE_NAME):
            raise FileNotFoundError("{} not found".format(CONFIG_FILE_NAME))

        with open(CONFIG_FILE_NAME, 'r') as source:
            yaml_content = yaml.safe_load(source.read())
            if not yaml_content:
                raise EmptyConfigFileError()
        self.background_dir = yaml_content.get(self.FIELD_BG_DIR, None)
        self.counters = yaml_content.get(self.FIELD_COUNTERS, [])
        self.mqtt_connection = yaml_content.get(self.FIELD_MQTT_CONNECTION)
        self.show_time = yaml_content.get(self.FIELD_SHOW_TIME)
