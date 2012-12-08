import sys
sys.path.append('..')
from base import AI
from random import randint


class Target(AI):
    def pulse(self):
        # raise Exception('lol')
        pass

    def init(self):
        pass
        while True:
            self.go(randint(-300, 300), randint(-300, 300)).wait()

target = Target()
target.color = 'orange'