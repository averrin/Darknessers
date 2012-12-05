from winterstone.base import *
import time
from PyQt4.QtCore import *


class AI(WinterObject, QObject):

    def __init__(self):
        WinterObject.__init__(self)
        QObject.__init__(self)

    def init(self):
        pass

    def pulse(self):
        pass

    def go(self, x, y):
        self.speed = 40
        self.ev = self.world.stream.addEvent(self._go(x, y))
        self.connect(self.ev, SIGNAL('moved(QPointF)'), self.move)

    def _go(self, x, y):
        start = self.object.pos()
        end = QPointF(x, y)
        l = QLineF(start, end).length()
        for c in range(0, int(l), 3):
            if self.stop:
                break
            time.sleep(1 / self.speed)
            t = c / l
            x = start.x() + (end.x() - start.x()) * t
            y = start.y() + (end.y() - start.y()) * t
            p = QPointF(x, y)

            self.emit(SIGNAL('moved(QPointF)'), p)

    @Slot(QPointF)
    def move(self, pos):
        self.object.setPos(pos)


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
                self.addEvent(ai.pulse)
            time.sleep(1 / self.speed)

    def addEvent(self, do):
        ev = Event(do)
        self.pool.append(ev)
        ev.start()
        return ev


class Event(QThread):
    def __init__(self, do):
        QThread.__init__(self)
        self.stop = False
        self.do = do

    def run(self):
        self.do()
