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
        self.rotator = False
        self.__skillpoints = 0
        self._speed = 20
        self.stopMove = False
        self.stopRotate_flag = False

    @property
    def speed(self):
        return self.api.getStats(self, 'speed')

    @property
    def lightr(self):
        return self.api.getStats(self, 'light')

    @property
    def angle(self):
        return self.api.getStats(self, 'angle')

    @property
    def pos(self):
        return self.api.getStats(self, 'pos')

    def rotate(self, angle):
        if not self.rotator or self.rotator.isFinished():
            self.rotator = self.world.stream.addEvent(lambda: self.world.rotateMe(angle), False)
            # print('Rotate', self.rotator, self.stopRotate_flag)
        else:
            self.stopRotate()
        return self.rotator

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
        if not self.mover or self.mover.isFinished():
            self.mover = self.world.stream.addEvent(lambda: self.world.moveMe(x, y), False)
        else:
            self.stop()
            # return self.go(x, y)
        return self.mover

    def stop(self):
        self.stopMove = True
        if self.mover:
            self.mover.wait()
        self.stopMove = False

    def stopRotate(self):
        self.stopRotate_flag = True
        if self.rotator:
            self.rotator.wait()
        self.stopRotate_flag = False


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
                    if self.isVisible(ai.pos):
                        ret.append(ai.pos)
        return ret

    def moveMe(self, x, y):  # Move logic
        if isinstance(self.ai, AI):
            start = self.ai.pos
            end = QPointF(x, y)
            l = QLineF(start, end).length()
            p = QPointF(x, y)
            d = 1 / float(self.ai.speed)
            clear = True
            for c in range(0, int(l), 3):
                if self.ai.stopMove or not clear:
                    break
                time.sleep(d)
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
                    probe = QLineF(self.ai.pos, end)
                    probe.setLength(20)
                    if not self.isVisible(probe.p2()):
                        # self.ai.api.drawPoint(probe.p2().x(), probe.p2().y())
                        time.sleep(d)
                    self.__original.stats[self.ai]['pos'] = p
                    self.ai.emit(SIGNAL('moved'), self.ai)
            self.ai.after_go(p.x(), p.y())
            self.ai.stopMove = False
            # self.ai.mover = False

    def isVisible(self, point):
        if QLineF(point, self.ai.pos).length() <= (self.ai.lightr):
            a = QLineF(point, self.ai.pos).angleTo(QLineF(self.ai.pos, QPointF(self.ai.pos.x(), self.ai.pos.y() + 1)))
            la = self.__original.stats[self.ai]['light_angle'] + self.ai.angle
            if a <= la / 2 or a >= 360 - la / 2:
                return True
            else:
                return False

    def rotateMe(self, angle):
        a = self.__original.stats[self.ai]['angle']
        if a < 0:
            self.__original.stats[self.ai]['angle'] = 360 + self.__original.stats[self.ai]['angle']
        if a > 360:
            self.__original.stats[self.ai]['angle'] = self.__original.stats[self.ai]['angle'] % 360
        a = self.__original.stats[self.ai]['angle']
        d = a - angle
        # print('Delta: %s' % d)
        dir = 1
#        if abs(d) > 180 and angle > 180:
 #           self.__original.stats[self.ai]['angle'] = 360 + self.__original.stats[self.ai]['angle']
  #          d = 360 - abs(d)
        if d > 0:
            dir = -1
        # print('Current: %s' % a)
        # print('Target: %s' % angle)
        # print('Delta: %s' % d)
        for i in range(1, abs(int(d))):
            if self.ai.stopRotate_flag:
                break
            self.__original.stats[self.ai]['angle'] += 1 * dir
            time.sleep(1 / float(self.ai.speed * 10))
            # print(self.__original.stats[self.ai]['angle'])

            self.ai.emit(SIGNAL('moved'), self.ai)
        self.ai.stopRotate_flag = False
        # self.ai.rotator = False


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
            # print(len(self.pool))
            # print(self.pool)
            for thread in self.pool:
                if thread.isFinished():
                    self.pool.remove(thread)
            time.sleep(1 / float(self.speed))

    def addEvent(self, do, inPool=True):
        ev = Event(do)
        # if inPool:
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

    def __repr__(self):
        return '%s - %s' % (repr(self.do), self.isFinished())
