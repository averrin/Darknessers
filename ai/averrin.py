import sys
sys.path.append('..')
from base import AI


class Averrin(AI):
    def pulse(self):
        pass

    def init(self):
        self.go(100, 100)

averrin = Averrin()
