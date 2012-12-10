import sys
sys.path.append('..')
from base import AI
from random import randint
from PyQt4.QtCore import *


class Target(AI):
    def __init__(self, *args, **kwargs):
        AI.__init__(self, *args, **kwargs)
        self.registerCallback('moved_callback', self.gotoRand)
        self.registerCallback('collision_callback', self.gotoRand)
        self.init = self.gotoRand

    def pulse(self):
        pass

    def gotoRand(self):
        p = QPointF(randint(-300, 300), randint(-300, 300))
        self.rotateTo(p)
        self.go(p.x(), p.y())

    def rotateTo(self, point):
        angle = QLineF(self.pos, point).angleTo(QLineF(QPointF(self.pos.x(), self.pos.y() + 1), self.pos))
        return self.rotate(angle)



target = Target()
target.color = 'orange'
