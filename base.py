from winterstone.base import *
import time
from PyQt4.QtCore import *
Slot = pyqtSlot


class AI(WinterObject, QObject):

    def __init__(self):
        WinterObject.__init__(self)
        QObject.__init__(self)
        self.mover = False
        self.__skillpoints = 0
        self._speed = 20
        self.__stop = False

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
            self.mover = self.world.stream.addEvent(lambda: self.__go(x, y))
            return self.mover
        else:
            self.stop()
            return self.go(x, y)

    def stop(self):
        self.__stop = True
        if self.mover:
            self.mover.wait()

    def __go(self, x, y):
        start = self.pos
        end = QPointF(x, y)
        l = QLineF(start, end).length()
        p = QPointF(x, y)
        for c in range(0, int(l), 3):
            if self.__stop:
                break
            time.sleep(1 / float(self.speed))
            t = c / l
            x = start.x() + (end.x() - start.x()) * t
            y = start.y() + (end.y() - start.y()) * t
            p = QPointF(x, y)

            self.emit(SIGNAL('moved(QPointF)'), p)
        self.__stop = False
        self.pos = p
        self.mover = False
        self.after_go(p.x(), p.y())


class World(WinterObject):
    def __init__(self, ai=''):
        WinterObject.__init__(self)
        if ai:
            self.ai = ai
            print('Generate world for %s' % ai)
        else:
            print('Generate global world')
            self.stats = {}


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
