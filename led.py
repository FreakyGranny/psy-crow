from threading import Thread
from time import sleep

import serial
from pyfirmata import Board, BOARDS

from parser import Message, LedTask, RgbColor
from mqtt import MESSAGE_EVENT


class ArduinoException(Exception):
    pass


class Arduino(Board):
    def __init__(self):
        self.connected = False

    def setup(self):
        port = self.discover_port()
        if not port:
            raise ArduinoException("No Arduino found")
        Board.__init__(self, port, layout=BOARDS['arduino'], baudrate=57600, name=None, timeout=None)
        self.connected = True

    @staticmethod
    def discover_port():
        locations = ['dev/ttyACM0', '/dev/ttyACM0', '/dev/ttyACM1',
                     '/dev/ttyACM2', '/dev/ttyACM3', '/dev/ttyACM4',
                     '/dev/ttyACM5', '/dev/ttyUSB0', '/dev/ttyUSB1',
                     '/dev/ttyUSB2', '/dev/ttyUSB3', '/dev/ttyUSB4',
                     '/dev/ttyUSB5', '/dev/ttyUSB6', '/dev/ttyUSB7',
                     '/dev/ttyUSB8', '/dev/ttyUSB9',
                     '/dev/ttyUSB10',
                     '/dev/ttyS0', '/dev/ttyS1', '/dev/ttyS2',
                     '/dev/tty.usbserial', '/dev/tty.usbmodem', 'com2',
                     'com3', 'com4', 'com5', 'com6', 'com7', 'com8',
                     'com9', 'com10', 'com11', 'com12', 'com13',
                     'com14', 'com15', 'com16', 'com17', 'com18',
                     'com19', 'com20', 'com21', 'com1'
                     ]
        detected = None

        for device in locations:
            try:
                serialport = serial.Serial(device, 57600, timeout=0)
                detected = device
                serialport.close()
                break
            except serial.SerialException:
                pass

        return detected


class ArduinoThread(Thread):
    BOARD_R_LED = 10
    BOARD_G_LED = 11
    BOARD_B_LED = 9

    STEPS_TO_FADE = 30
    FADE_TIMEOUT = 0.1

    def __init__(self, root, led_queue, message_queue):
        Thread.__init__(self)
        self.root = root
        self.queue = led_queue
        self.message_queue = message_queue
        self.is_last_state_firing = False
        self.board = Arduino()
        self.red_pin = None
        self.green_pin = None
        self.blue_pin = None

        self.is_light_on = False
        self.is_fade_out = False
        self.color = RgbColor((0, 0, 0))
        self.current_color = RgbColor((0, 0, 0))
        self.steps = RgbColor((0, 0, 0))
        self.last_step = 0
        self.led_time = 0.0
        self.timer = 0.0

    def _setup(self):
        self.board.setup()
        self.red_pin = self.board.get_pin('d:{}:p'.format(self.BOARD_R_LED))
        self.green_pin = self.board.get_pin('d:{}:p'.format(self.BOARD_G_LED))
        self.blue_pin = self.board.get_pin('d:{}:p'.format(self.BOARD_B_LED))

    def apply_led_light(self):
        self.red_pin.write(1.0 - self.current_color[RgbColor.RED] / 255)
        self.green_pin.write(1.0 - self.current_color[RgbColor.GREEN] / 255)
        self.blue_pin.write(1.0 - self.current_color[RgbColor.BLUE] / 255)

    def set_led_options(self, task: LedTask):
        if task.is_firing == self.is_last_state_firing:
            return
        self.is_last_state_firing = task.is_firing

        self.color = task.rgb_color
        self.led_time = task.seconds
        self.timer = 0.0
        for level_key, level_value in task.rgb_color.items():
            level_value = level_value / self.STEPS_TO_FADE
            self.steps[level_key] = level_value
        self.is_light_on = True
        self.is_fade_out = False

    def fade(self):
        modifier = -1 if self.is_fade_out else 1

        for step in range(0, 5):
            self.last_step += 1

            if self.last_step > self.STEPS_TO_FADE:
                self.is_fade_out = not self.is_fade_out
                self.last_step = 0
                break

            for level_key in self.current_color.keys():
                level_value = self.current_color[level_key] + modifier * self.steps[level_key]

                level_value = self.color[level_key] if level_value > self.color[level_key] else level_value
                level_value = 255 if level_value > 255 else level_value
                level_value = 0 if level_value < 0 else level_value

                self.current_color[level_key] = int(level_value)
            self.apply_led_light()
            sleep(self.FADE_TIMEOUT)
            self.timer += self.FADE_TIMEOUT

    def check_timer(self):
        if self.led_time == 0:
            return

        if self.timer >= self.led_time:
            self.is_light_on = False
            self.timer = 0.0
            self.current_color = RgbColor((0, 0, 0))
            self.apply_led_light()

    def run(self):
        sleep(1)
        message = "Arduino successfully connected"
        try:
            self._setup()
        except ArduinoException as e:
            message = str(e)
        self.message_queue.put(
            Message(
                title="System",
                text=message,
                color="#707070"
            )
        )
        if self.root:
            self.root.event_generate(MESSAGE_EVENT)

        if not self.board.connected:
            return

        # turn off led
        self.red_pin.write(1.0)
        self.green_pin.write(1.0)
        self.blue_pin.write(1.0)

        while True:
            if not self.queue.empty():
                self.set_led_options(self.queue.get_nowait())

            if not self.is_light_on:
                sleep(0.5)
                continue

            self.fade()
            self.check_timer()
