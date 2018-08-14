import json

FIELD_LED = "led"
FIELD_LED_COLOR = "color"
FIELD_LED_SECONDS = "seconds"

FIELD_MESSAGES = "messages"
FIELD_MESSAGES_COLOR = "color"
FIELD_MESSAGES_TITLE = "title"
FIELD_MESSAGES_TEXT = "text"
FIELD_MESSAGES_RESOLVE_COLOR = "resolve_color"


class LedTask:
    def __init__(self, hex_color, seconds):
        self.hex_color = hex_color.upper()
        self.seconds = seconds

    @property
    def rgb_color(self):
        # todo this function should return color in RGB
        return 255, 0, 0


class Message:
    def __init__(self, title, text, color, resolve_color=None):
        self.title = title
        self.text = text
        self.color = color.upper()
        self.resolve_color = resolve_color.upper() if resolve_color else resolve_color


def get_led_options(json_message):
    data = json.loads(json_message)
    led_section = data.get(FIELD_LED)
    if not led_section:
        return

    return LedTask(
        hex_color=led_section.get(FIELD_LED_COLOR, "#000000"),
        seconds=led_section.get(FIELD_LED_SECONDS, 1)
    )


def get_messages(json_message):
    data = json.loads(json_message)
    messages_section = data.get(FIELD_MESSAGES)
    if not messages_section:
        return []

    for message in messages_section:
        yield Message(
            title=message.get(FIELD_MESSAGES_TITLE, "None"),
            text=message.get(FIELD_MESSAGES_TEXT, "None"),
            color=message.get(FIELD_MESSAGES_COLOR, "#FFFFFF"),
            resolve_color=message.get(FIELD_MESSAGES_RESOLVE_COLOR, "#FFFFFF"),
        )
