from winterstone.base import *
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
Slot = pyqtSlot


class AI(WinterObject, QObject):

    def __init__(self):
        WinterObject.__init__(self)
        QObject.__init__(self)
        self.mover = False
        self.__skillpoints = 0
        self._speed = 20
        self.stopMove = False

    @property
    def speed(self):
        return self.api.getStats(self, 'speed')

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
        if not self.mover:
            self.mover = self.world.stream.addEvent(lambda: self.world.moveMe(self, x, y))
            return self.mover
        else:
            self.stop()
            return self.go(x, y)

    def stop(self):
        self.stopMove = True
        if self.mover:
            self.mover.wait()


class Barrier(QPolygonF):
    pass


class World(WinterObject):
    def __init__(self, ai='', original=''):
        WinterObject.__init__(self)
        if ai:
            self.ai = ai
            self.__original = original
            print('Generate world for %s' % ai)
        else:
            print('Generate global world')
            self.stats = {}
            self.ai = []
            self.barriers = []
            self.__original = self

    def getBarriers(self):
        return self.__original.barriers

    def moveMe(self, obj, x, y):
        start = obj.pos
        end = QPointF(x, y)
        l = QLineF(start, end).length()
        p = QPointF(x, y)
        for c in range(0, int(l), 3):
            if obj.stopMove:
                break
            time.sleep(1 / float(obj.speed))
            t = c / l
            x = start.x() + (end.x() - start.x()) * t
            y = start.y() + (end.y() - start.y()) * t
            p = QPointF(x, y)

            obj.emit(SIGNAL('moved(QPointF)'), p)
        obj.stopMove = False
        obj.pos = p
        obj.mover = False
        obj.after_go(p.x(), p.y())


class Stream(QThread):
    def __init__(self, ai):
        QThread.__init__(self)
        self.__stop = False
        self.ai = ai
        self.pool = []
        self.speed = 40

    def run(self):
        while not self.__stop:
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
        # try:
        self.do()
        # except:
            # pass
