import sys
sys.path.append('..')
from base import AI
import time
from random import randint
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class Averrin(AI):
    def pulse(self):
        pass
        if hasattr(self, 'world'):
            partner = self.world.getAI()
            # return
            # self.api.drawPoint(self.pos.x(), self.pos.y(), color="green")
            if partner:
                p = partner[0]
                if QLineF(p, self.pos).length() < QLineF(self.waypoint, self.pos).length():
                    self.rotateTo(p)
                    self.stop()

    def init(self):
        self.waypoint = self.pos
        # return
        while True:
            partner = self.world.getAI()
            #partner = False
            if partner:
                lg = QColor('lightgreen')
                lg.setAlpha(100)
                self.object.lc.setBrush(QBrush(lg))
                self.goto(partner[0])
                pass
            else:
                yl = QColor('yellow')
                yl.setAlpha(100)
                self.object.lc.setBrush(QBrush(yl))
                self.goto(QPointF(randint(-300, 300), randint(-300, 300)))

    def goto(self, target):
        self.waypoint = target
        g = self.go(self.waypoint.x(), self.waypoint.y())
        r = self.rotateTo(self.waypoint)
        g.wait()
        # r.wait()

    def before_go(self, x, y):
        self.target = self.api.drawPoint(x, y)
        self.path = self.api.drawLine(self.pos.x(), self.pos.y(), x, y)

    def after_go(self, x, y):
        self.target.hide()
        self.path.hide()

    def collision_go(self, x, y):
        self.api.drawPoint(x, y)

    def rotateTo(self, point):
        angle = QLineF(self.pos, self.waypoint).angleTo(QLineF(QPointF(self.pos.x(), self.pos.y() + 1), self.pos))
        print(angle)
        return self.rotate(angle)

averrin = Averrin()
averrin.color = 'violet'
