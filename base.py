from winterstone.base import *
import time
from PyQt4.QtCore import *
Slot = pyqtSlot


class AI(WinterObject, QObject):

    def __init__(self):
        WinterObject.__init__(self)
        QObject.__init__(self)
        self.busy = False
        self.speed = 10
        self.stop = False

    def init(self):
        pass

    def pulse(self):
        pass

    def go(self, x, y):
        if not self.busy:
            self.ev = self.world.stream.addEvent(lambda: self._go(x, y))
            # print 'start', self.ev
            return self.ev
        else:
            pass
            # print 'busy'
        # self.connect(self.ev, SIGNAL('moved(QPointF)'), self.move)

    def _go(self, x, y):
        print self
        self.busy = True
        start = self.pos
        end = QPointF(x, y)
        l = QLineF(start, end).length()
        for c in range(0, int(l), 3):
            if self.stop:
                break
            time.sleep(0.05)
            t = c / l
            x = start.x() + (end.x() - start.x()) * t
            y = start.y() + (end.y() - start.y()) * t
            p = QPointF(x, y)

            self.emit(SIGNAL('moved(QPointF)'), p)
        self.busy = False
        self.pos = end

    # @Slot(QPointF)
    # def move(self, pos):
    #     print pos
    #     self.object.setPos(pos)


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
