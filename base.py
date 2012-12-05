from winterstone.base import *
import time
from PyQt4.QtCore import *


class AI(WinterObject):

    def pulse(self):
        pass


class World(Borg):
    pass


class Stream(QThread):
    def __init__(self, ai):
        QThread.__init__(self)
        self.stop = False
        self.ai = ai
        self.pool = []
        self.speed = 40

    def run(self):
        while not self.stop:
            for ai in self.ai:
                ev = Event(ai.pulse)
                self.pool.append(ev)
                ev.start()
            time.sleep(1 / self.speed)


class Event(QThread):
    def __init__(self, do):
        QThread.__init__(self)
        self.stop = False
        self.do = do

    def run(self):
        self.do()
