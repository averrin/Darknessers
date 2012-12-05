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
            self.go(100, 0)
            time.sleep(0.3)
            self.stop()  # for after_go callback
            self.__skillpoints = 55
            self.speed += 5
            self._speed += 5
            self.go(0, 0).wait()
            self.go(0, 100).wait()

    def before_go(self, x, y):
        self.target = self.api.drawPoint(x, y)
        self.path = self.api.drawLine(self.pos.x(), self.pos.y(), x, y)

    def after_go(self, x, y):
        self.target.hide()
        self.path.hide()

averrin = Averrin()
