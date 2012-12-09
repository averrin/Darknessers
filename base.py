from winterstone.base import *
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
Slot = pyqtSlot


class AI(WinterObject, QObject):
    """
        Base class for ai
    """

    moved_callback = pyqtSignal(name="moved_callback")
    collision_callback = pyqtSignal(name="collision_callback")

    def __init__(self):
        WinterObject.__init__(self)
        self.mover = False
        self.rotator = False
        self.__skillpoints = 0
        self._speed = 20
        self.stopMove = False
        self.stopRotate_flag = False
        self.callbacks = {}

        QObject.__init__(self)

    def registerCallback(self, signal, callback):  # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # print(signal, callback, signal in self.callbacks.keys())
        # if signal in self.callbacks:
        #     print('!!!!!!!!!!!!!!!!')
        # try:
        #     signal.disconnect()
        # except Exception as e:
        #     print(e)
        # print(dir(signal), signal.signal)
        if signal.signal in self.callbacks:
            signal.disconnect(self.callbacks[signal.signal])
        self.callbacks[signal.signal] = callback
        signal.connect(callback)
        # print(self.callbacks)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

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
        self.emit(SIGNAL('rotate'), angle)

    def init(self):
        pass

    def pulse(self):
        pass

    def before_go(self, x, y):
        pass

    def after_go(self):
        pass

    def collision_go(self, x, y):
        pass

    def go(self, x, y):
        self.before_go(x, y)
        self.emit(SIGNAL('goto'), x, y)

    def stop(self):
        self.stopMove = True

    def stopRotate(self):
        self.stopRotate_flag = True


class Barrier(QPolygonF):
    pass


class World(WinterObject):
    def __init__(self, ai='', original='', stream=''):
        WinterObject.__init__(self)
        if ai:  # Personal world
            self.ai = ai
            ai.connect(ai, SIGNAL('goto'), self.startMove)
            ai.connect(ai, SIGNAL('rotate'), self.startRotate)
            self.__original = original
            QObject.connect(self.__original.stream.emmiter, SIGNAL('addEvent'), self.addEvent)
            print('Generate world for %s' % ai)
        else:  # Global world
            print('Generate global world')
            self.stats = {}
            self.ai = []
            self.barriers = []
            self.__original = self
            self.stream = stream

    def startMove(self, x, y):
        if not self.ai.mover or self.ai.mover.isFinished():
            self.ai.mover = self.addEvent(lambda: self.moveMe(x, y))

    def startRotate(self, angle):
        if not self.ai.rotator or self.ai.rotator.isFinished():
            self.ai.rotator = self.addEvent(lambda: self.rotateMe(angle))

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
                if not self.ai.stopMove:
                    time.sleep(d)
                    t = c / l
                    x = start.x() + (end.x() - start.x()) * t
                    y = start.y() + (end.y() - start.y()) * t
                    p = QPointF(x, y)
                    for b in self.__original.barriers:
                        if b.containsPoint(p, Qt.OddEvenFill | Qt.WindingFill):
                            self.ai.stopMove = True
                            clear = False
                            # break
                    if clear:
                        probe = QLineF(self.ai.pos, end)
                        probe.setLength(20)
                        if not self.isVisible(probe.p2()):
                            time.sleep(d)
                        self.__original.stats[self.ai]['pos'] = p
                        self.ai.emit(SIGNAL('moved'), self.ai)

            if not self.ai.stopMove:
                self.ai.stopMove = False
                if self.ai.color == 'violet':
                    print('Before moved callback for %s' % self.ai)
                self.ai.moved_callback.emit()
                # self.ai.emit(SIGNAL('moved_callback'))
            elif not clear:
                self.ai.stopMove = False
                self.ai.collision_callback.emit()

    def isVisible(self, point):
        if QLineF(point, self.ai.pos).length() <= (self.ai.lightr):
            a = QLineF(point, self.ai.pos).angleTo(QLineF(self.ai.pos, QPointF(self.ai.pos.x(), self.ai.pos.y() + 1)))
            la = self.__original.stats[self.ai]['light_angle'] + self.ai.angle
            if a <= la / 2 or a >= 360 - la / 2:
                return True
            else:
                return False
                self.ai.api.drawPoint(point.x(), point.y())

    def rotateMe(self, angle):
        if isinstance(self.ai, AI):
            a = self.__original.stats[self.ai]['angle']
            if a < 0:
                self.__original.stats[self.ai]['angle'] = 360 + self.__original.stats[self.ai]['angle']
            if a > 360:
                self.__original.stats[self.ai]['angle'] = self.__original.stats[self.ai]['angle'] % 360
            a = self.__original.stats[self.ai]['angle']
            d = a - angle
            dir = 1

            if d > 0:
                dir = -1

            for i in range(1, abs(int(d))):
                if not self.ai.stopRotate_flag:
                    self.__original.stats[self.ai]['angle'] += 1 * dir
                    time.sleep(1 / float(self.ai.speed * 10))

                    self.ai.emit(SIGNAL('moved'), self.ai)
            self.ai.stopRotate_flag = False

    def addEvent(self, do):
        ev = Event(do)
        self.stream.pool.append(ev)
        ev.start()
        return ev


class Stream(QThread):
    def __init__(self, ai):
        QThread.__init__(self)
        self.__stop = False
        self.ai = ai
        self.pool = []
        self.speed = 2
        self.emmiter = QObject()

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
        self.emmiter.emit(SIGNAL('addEvent'), do)

    def stop(self):
        self.__stop = True


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
