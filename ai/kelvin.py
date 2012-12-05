import sys
sys.path.append('..')
from base import AI


class Kelvin(AI):
    def pulse(self):
        print 'kelvin'

kelvin = Kelvin()
