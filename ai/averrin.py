import sys
sys.path.append('..')
from base import AI
import time
from random import randint


class Averrin(AI):
    def pulse(self):
        pass

    def init(self):
        print(map(lambda x: [(x.at(i).x(), x.at(i).y()) for i in range(0, x.count())], self.world.getBarriers()))
        while True:
            partner = self.world.getAI()
            self.go(partner[0].pos.x(), partner[0].pos.y()).wait()

    # def before_go(self, x, y):
    #     self.target = self.api.drawPoint(x, y)
    #     self.path = self.api.drawLine(self.pos.x(), self.pos.y(), x, y)

    # def after_go(self, x, y):
    #     self.target.hide()
    #     self.path.hide()

    def collision_go(self, x, y):
        self.api.drawPoint(x, y)

averrin = Averrin()
averrin.color = 'violet'
