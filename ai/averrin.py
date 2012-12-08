import sys
sys.path.append('..')
from base import AI
import time
from random import randint
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Mode(object):
    def __init__(self, ai):
        self.ai = ai

    def activate(self):
        pass

    def deactivate(self):
        pass

    def onPulse(self):
        pass


class FreeMode(Mode):
    def activate(self):
        color = QColor('yellow')
        color.setAlpha(100)
        self.ai.object.lc.setBrush(QBrush(color))
        print('Im free!')
        p = QPointF(randint(-300, 300), randint(-300, 300))
        self.ai.goto(p)

    def onPulse(self):
        targets = self.ai.world.getAI()
        if targets:
            self.ai.changeMode('stalker')
        elif self.ai.mover and self.ai.mover.isFinished():
            p = QPointF(randint(-300, 300), randint(-300, 300))
            self.ai.goto(p)


class StalkerMode(Mode):
    def activate(self):
        self.hist = ['', '']
        color = QColor('green')
        color.setAlpha(100)
        self.ai.object.lc.setBrush(QBrush(color))
        print('Stalker!!!')
        self.ai.stop()

    def onPulse(self):
        # if self.ai.mover and self.ai.mover.isFinished():
        targets = self.ai.world.getAI()
        if not targets:
            pass
            if len(self.hist) == 2:
                predct = QLineF(self.hist[0], self.hist[1])
                predct.setLength(30)
                target = predct.p2()
                self.ai.goto(target)
                time.sleep((1 / self.ai.speed) * 20)
                # self.ai.stop()
            else:
                self.ai.changeMode('free')
        else:
            if self.hist[1]:
                predct = QLineF(self.hist[1], targets[0])
                predct.setLength(30)
                self.hist[0] = self.hist[1]
                self.hist[1] = targets[0]
                target = predct.p2()
            else:
                target = targets[0]
                self.hist[1] = targets[0]
            if self.ai.mover.isFinished():
                # self.ai.stop()
                # self.ai.mover.wait()
                self.ai.goto(target)
                time.sleep((1 / self.ai.speed) * 20)
                # self.ai.stop()




class Averrin(AI):

    def __init__(self, *args, **kwargs):
        AI.__init__(self, *args, **kwargs)

        self.modes = {'free': FreeMode(self), 'stalker': StalkerMode(self)}
        self.mode = False
        self.ready = False

    def changeMode(self, mode_name):
        if self.mode:
            self.mode.deactivate()
        self.mode = self.modes[mode_name]
        print('Activate "%s" mode' % mode_name)
        self.mode.activate()

    def pulse(self):
        if self.mode:
            self.mode.onPulse()

    def init(self):
        self.ready = True
        self.changeMode('free')

    def goto(self, target):
        self.waypoint = target
        self.stopRotate()
        # g.wait()
        self.rotateTo(self.waypoint)
        self.go(self.waypoint.x(), self.waypoint.y()).wait()
        self.rotator.wait()

    def before_go(self, x, y):
        self.target = self.api.drawPoint(x, y)
        # self.path = self.api.drawLine(self.pos.x(), self.pos.y(), x, y)

    def after_go(self, x, y):
        self.target.hide()
        # self.path.hide()

    def collision_go(self, x, y):
        self.api.drawPoint(x, y)

    def rotateTo(self, point):
        angle = QLineF(self.pos, point).angleTo(QLineF(QPointF(self.pos.x(), self.pos.y() + 1), self.pos))
        return self.rotate(angle)

averrin = Averrin()
averrin.color = 'violet'
