from winterstone.base import *
import time
from PyQt4.QtCore import *
Slot = pyqtSlot


class AI(WinterObject, QObject):

    def __init__(self):
        WinterObject.__init__(self)
        QObject.__init__(self)
        self.mover = False
        self.speed = 20
        self._stop = False

    def init(self):
        pass

    def pulse(self):
        pass

    def before_go(self, x, y):
        pass

    def after_go(self, x, y):
        pass

    def go(self, x, y):
        self.before_go(x, y)
        print(self.pos)
        if not self.mover:
            self.mover = self.world.stream.addEvent(lambda: self._go(x, y))
            return self.mover
        else:
            self.stop()
            return self.go(x, y)

    def stop(self):
        self._stop = True
        if self.mover:
            self.mover.wait()

    def _go(self, x, y):
        print('Start mover', self)
        start = self.pos
        end = QPointF(x, y)
        l = QLineF(start, end).length()
        p = QPointF(x, y)
        for c in range(0, int(l), 3):
            if self._stop:
                print('Stop mover', self)
                break
            time.sleep(1 / float(self.speed))
            t = c / l
            x = start.x() + (end.x() - start.x()) * t
            y = start.y() + (end.y() - start.y()) * t
            p = QPointF(x, y)

            self.emit(SIGNAL('moved(QPointF)'), p)
        self._stop = False
        self.pos = p
        self.mover = False
        self.after_go(p.x(), p.y())



class World(Borg):
    pass


class Stream(QThread):
    def __init__(self, ai):
        QThread.__init__(self)
        self.stop = False
        self.ai = ai
        self.pool = []
        self.speed = 20

    def run(self):
        while not self.stop:
            for ai in self.ai:
                self.addEvent(ai.pulse)
            time.sleep(1 / float(self.speed))

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
