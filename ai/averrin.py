import sys
sys.path.append('..')
from base import AI
import time
from random import randint
from PyQt4.QtCore import *


class Averrin(AI):
    def pulse(self):
        if hasattr(self, 'world'):
            partner = self.world.getAI()
            self.api.drawPoint(self.pos.x(), self.pos.y(), color="green")
            if partner:
                p = partner[0]
                if QLineF(p, self.pos).length() < QLineF(self.waypoint, self.pos).length():
                    self.stop()

    def init(self):
        self.waypoint = self.pos
        print(map(lambda x: [(x.at(i).x(), x.at(i).y()) for i in range(0, x.count())], self.world.getBarriers()))
        while True:
            partner = self.world.getAI()
            if partner:
                self.waypoint = QPointF(partner[0].x(), partner[0].y())
                self.go(partner[0].x(), partner[0].y()).wait()
            else:
                self.waypoint = QPointF(randint(-300, 300), randint(-300, 300))
                self.go(self.waypoint.x(), self.waypoint.y()).wait()

    def before_go(self, x, y):
        self.target = self.api.drawPoint(x, y)
        self.path = self.api.drawLine(self.pos.x(), self.pos.y(), x, y)

    def after_go(self, x, y):
        self.target.hide()
        self.path.hide()

    def collision_go(self, x, y):
        self.api.drawPoint(x, y)

averrin = Averrin()
averrin.color = 'violet'
