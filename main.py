#!/usr/bin/env python
# -*- coding: utf-8 -*-c
from __future__ import print_function, unicode_literals
import json
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.base import *
from loader import Loader
from base import AI, World, Stream
from winterstone.snowflake import loadIcons


class API(WinterAPI):
    def __init__(self, scene):
        WinterAPI.__init__(self)
        self.__scene = scene

    def drawPoint(self, x, y, color='red', r=2):
        return self.__scene.addEllipse(QRectF(QPointF(x - (r / 2), y - (r / 2)), QPointF(x + (r / 2), y + (r / 2))), QPen(QColor(color)))

    def drawLine(self, x, y, x1, y1, color='blue'):
        l = QGraphicsLineItem(QLineF(QPointF(x, y), QPointF(x1, y1)))
        l.setPen(QPen(QColor(color)))
        self.__scene.addItem(l)
        return l


class UI(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle(u"Darknessers")
        self.setWindowIcon(QIcon('static/bulb.png'))
        self.resize(QSize(800, 600))

        scene = QGraphicsScene()
        self.scene = scene

        widget = QGraphicsView()
        widget.setScene(scene)

        self.setCentralWidget(widget)

        self.api = API(scene)
        self.api.addIconsFolder('static')
        self.api.addIconsFolder('static/emblems')

        self.drawDots()
        self.loadAI()
        print(AI.objects.all())
        self.stream = Stream(self.ai)
        self.stream.start()
        self.world = World()

        for ai in self.ai:
            ai.world = World(ai)
            ai.world.stream = self.stream
            ai.api = self.api
            em = QGraphicsPixmapItem(QPixmap(self.api.icons['pink']))
            em.setPos((qrand() % 50) * (qrand() % 2), (qrand() % 50) * (qrand() % 2))
            em.setOffset(-10, -10)
            ai.object = em
            ai.pos = em.pos()
            self.scene.addItem(em)
            self.connect(ai, SIGNAL('moved(QPointF)'), lambda x: self.moveEm(em, x))
            ai.skillpoints = 5
            self.stream.addEvent(ai.init)

    def moveEm(self, em, pos):
        em.setPos(pos)

    def drawDots(self):
        tl = QPoint(-300, -300)
        br = QPoint(300, 300)
        step = 20
        for x in range(tl.x(), br.x(), step):
            for y in range(tl.y(), br.y(), step):
                e = self.scene.addEllipse(QRectF(QPointF(x, y), QPointF(x + 0.5, y + 0.5)), QPen(QColor('#555')))
                e.setZValue(-60)

    def loadAI(self):
        self.loader = Loader(AI, 'ai')
        self.ai = self.loader.modules


def main():
    qtapp = QApplication(sys.argv)
    win = UI()
    win.show()
    qtapp.exec_()


if __name__ == '__main__':
    main()
