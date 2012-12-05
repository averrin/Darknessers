import sys
sys.path.append('..')
from base import AI


class Kelvin(AI):
    def pulse(self):
        raise Exception('lol')

kelvin = Kelvin()
