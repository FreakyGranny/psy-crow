import json

FIELD_COUNTERS = "counters"

FIELD_MESSAGES = "messages"
FIELD_MESSAGES_SEVERITY = "severity"
FIELD_MESSAGES_TITLE = "title"
FIELD_MESSAGES_TEXT = "text"
FIELD_MESSAGES_RESOLVED = "resolved"


class RgbColor(dict):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

    def __init__(self, colors: tuple):
        super().__init__(
            {
                self.RED: colors[0],
                self.GREEN: colors[1],
                self.BLUE: colors[2],
            }
        )

#
# class LedTask:
#     def __init__(self, hex_color, is_firing, seconds):
#         self.hex_color = hex_color.upper()
#         self.seconds = seconds
#         self.is_firing = is_firing
#         self.rgb_color = RgbColor(tuple(int(self.hex_color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4)))


class Message:
    def __init__(self, title, text, color):
        self.title = title
        self.text = text
        self.color = color.upper()


# def get_led_options(data):
#     return LedTask(
#         hex_color=data.get(FIELD_LED_COLOR, "#000000"),
#         is_firing=data.get(FIELD_LED_IS_FIRING, False),
#         seconds=0 if data.get(FIELD_LED_IS_FIRING, False) else 60
#     )


def get_counters(data):
    return data.get(FIELD_COUNTERS, {})


def get_messages(config, json_message):
    data = json.loads(json_message)
    messages_section = data.get(FIELD_MESSAGES)
    if not messages_section:
        return []

    for message in messages_section:
        severity = message.get(FIELD_MESSAGES_SEVERITY, "")
        if message.get(FIELD_MESSAGES_RESOLVED, False):
            severity = FIELD_MESSAGES_RESOLVED
        yield Message(
            title=message.get(FIELD_MESSAGES_TITLE, "None"),
            text=message.get(FIELD_MESSAGES_TEXT, "None"),
            color=config.get_color(severity),
        )
