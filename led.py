
class LedTask:
    def __init__(self, hex_color, seconds):
        self.hex_color = hex_color.upper()
        self.seconds = seconds

    @property
    def rgb_color(self):
        # todo this function should return color in RGB
        return 255, 0, 0
