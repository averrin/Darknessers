import sys
sys.path.append('..')
from base import AI


class Averrin(AI):
    def pulse(self):
        print 'averrin'

averrin = Averrin()
