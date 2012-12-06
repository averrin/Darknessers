import sys
sys.path.append('..')
from base import AI
from random import randint


class Kelvin(AI):
    def pulse(self):
        # raise Exception('lol')
        pass

    def init(self):
        while True:
            self.go(randint(-300, 300), randint(-300, 300)).wait()

kelvin = Kelvin()
