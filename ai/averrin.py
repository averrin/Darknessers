import sys
sys.path.append('..')
from base import AI
import time


class Averrin(AI):
    def pulse(self):
        pass

    def init(self):
        while True:
            self.go(100, 100).wait()
            self.go(100, 0).wait()
            self.go(0, 0).wait()
            self.go(0, 100).wait()

averrin = Averrin()
