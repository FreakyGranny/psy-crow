from threading import Thread
from time import sleep

import serial
from pyfirmata import Board, BOARDS

from parser import Message
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
    BOARD_LED = 9

    def __init__(self, root, led_queue, message_queue):
        Thread.__init__(self)
        self.root = root
        self.queue = led_queue
        self.message_queue = message_queue
        self.board = Arduino()

    def _setup(self):
        self.board.setup()

    def turn_on(self):
        self.board.digital[self.BOARD_LED].write(1)

    def turn_off(self):
        self.board.digital[self.BOARD_LED].write(0)

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
        self.root.event_generate(MESSAGE_EVENT)

        if not self.board.connected:
            return

        while True:
            sleep(1)
            if self.queue.empty():
                continue

            task = self.queue.get_nowait()
            if task.seconds == 0:
                self.turn_on()
            else:
                self.turn_off()

