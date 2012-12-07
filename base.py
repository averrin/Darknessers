from winterstone.base import *
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
Slot = pyqtSlot


class AI(WinterObject, QObject):
    """
        Base class for ai
    """

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

    @property
    def lightr(self):
        return self.api.getStats(self, 'light')

    @property
    def angle(self):
        return self.api.getStats(self, 'angle')

    def rotate(self, angle):
        self.api.rotate(self, angle)

    def init(self):
        pass

    def pulse(self):
        pass

    def before_go(self, x, y):
        pass

    def after_go(self, x, y):
        pass

    def collision_go(self, x, y):
        pass

    def go(self, x, y):
        self.before_go(x, y)
        if not self.mover:
            self.mover = self.world.stream.addEvent(lambda: self.world.moveMe(x, y))
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
        if ai:  # Personal world
            self.ai = ai
            self.__original = original
            print('Generate world for %s' % ai)
        else:  # Global world
            print('Generate global world')
            self.stats = {}
            self.ai = []
            self.barriers = []
            self.__original = self

    def getBarriers(self):  # Visible barriers
        return map(lambda x: [x.at(i) for i in range(0, x.count())], self.__original.barriers)
        pass  # TODO: visibility

    def getAI(self):  # Visible enimies
        ret = []
        if hasattr(self.ai, 'pos'):
            for ai in self.__original.ai:
                if ai is not self.ai and hasattr(ai, 'pos'):
                    if QLineF(ai.pos, self.ai.pos).length() <= (self.ai.lightr): # + ai.lightr / 2):
                        a = QLineF(ai.pos, self.ai.pos).angleTo(QLineF(self.ai.pos, QPointF(self.ai.pos.x(), self.ai.pos.y()+1)))
                        _a = abs(self.ai.angle - 90)
                        la = self.__original.stats[self.ai]['light_angle'] + self.ai.angle
                        if a < la / 2 or a > 360 - la / 2:
                            ret.append(ai.pos)
                            ai.api.drawPoint(ai.pos.x(), ai.pos.y(), color="orange")
        return ret  # TODO: visibility

    def moveMe(self, x, y):  # Move logic
        if isinstance(self.ai, AI):
            start = self.ai.pos
            end = QPointF(x, y)
            l = QLineF(start, end).length()
            p = QPointF(x, y)
            clear = True
            for c in range(0, int(l), 3):
                if self.ai.stopMove or not clear:
                    break
                time.sleep(1 / float(self.ai.speed))
                t = c / l
                x = start.x() + (end.x() - start.x()) * t
                y = start.y() + (end.y() - start.y()) * t
                p = QPointF(x, y)
                for b in self.__original.barriers:
                    if b.containsPoint(p, Qt.OddEvenFill | Qt.WindingFill):
                        self.ai.collision_go(x, y)
                        self.ai.stopMove = True
                        clear = False
                        # break
                if clear:
                    self.ai.pos = QPointF(x, y)
                    self.ai.emit(SIGNAL('moved'), self.ai)
            self.ai.stopMove = False
            self.ai.mover = False
            self.ai.after_go(p.x(), p.y())

    def isVisible(self, point):
        return True


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
                self.addEvent(ai.pulse)  # heartbeat
            for thread in self.pool:
                if thread.isFinished():
                    self.pool.remove(thread)
            time.sleep(1 / float(self.speed))

    def addEvent(self, do):
        ev = Event(do)
        self.pool.append(ev)
        ev.start()
        return ev


class Event(QThread):  # Event on separate thread
    def __init__(self, do):
        QThread.__init__(self)
        self.stop = False
        self.do = do

    def run(self):
        # try:
        self.do()
        # except:
            # pass
