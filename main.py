#!/usr/bin/env python
# -*- coding: utf-8 -*-c
from __future__ import print_function, unicode_literals
import json
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.base import *
from loader import Loader
from base import AI, World, Stream, Barrier
from winterstone.snowflake import loadIcons
from random import randint


class API(WinterAPI):
    def __init__(self, scene, world):
        WinterAPI.__init__(self)
        self.__scene = scene
        self.__world = world

    def drawPoint(self, x, y, color='red', r=2):
        return self.__scene.addEllipse(QRectF(QPointF(x - (r / 2), y - (r / 2)), QPointF(x + (r / 2), y + (r / 2))), QPen(QColor(color)))

    def drawLine(self, x, y, x1, y1, color='blue'):
        l = QGraphicsLineItem(QLineF(QPointF(x, y), QPointF(x1, y1)))
        l.setPen(QPen(QColor(color)))
        self.__scene.addItem(l)
        return l

    def getStats(self, who, stat):
        return self.__world.stats[who][stat]

    def addStats(self, who, stat):
        if self.__world.stats[who]['skillpoints'] > 0:
            self.__world.stats[who]['skillpoints'] -= 1
            self.__world.stats[who][stat] += 1


class UI(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("Darknessers")
        self.setWindowIcon(QIcon('static/bulb.png'))
        self.resize(QSize(800, 600))

        scene = QGraphicsScene()
        self.scene = scene

        widget = QGraphicsView()
        # restart = QPushButton('Restart')
        # restart.clicked.connect(self.start)
        # widget.setLayout(QHBoxLayout())
        # widget.layout().addWidget(restart)
        widget.setScene(scene)

        self.setCentralWidget(widget)

        self.start()

    def start(self):
        self.scene.clear()
        self.drawDots()
        self.loadAI()
        self.stream = Stream(self.ai)
        self.stream.start()
        self.world = World()
        self.world.ai = self.ai
        self.initWorld()
        self.api = API(self.scene, self.world)
        self.api.addIconsFolder('static')
        self.api.addIconsFolder('static/emblems')
        self.initAI()

    def initAI(self):
        for ai in self.ai:
            ai.world = World(ai, self.world)
            self.world.stats[ai] = {
                'speed': 20,
                'skillpoints': 5,
                'hp': 50,
                'ac': 10,
                'light': 50
            }
            ai.world.stream = self.stream
            ai.api = self.api
            cont = QGraphicsPolygonItem()
            cont.setPos(randint(-50, 50), randint(-50, 50))
            ai.object = cont
            cont.ai = ai
            ai.pos = cont.pos()
            lc = QGraphicsEllipseItem(QRectF(QPointF(-ai.lightr, -ai.lightr), QSizeF(ai.lightr * 2, ai.lightr * 2)), cont)
            yl = QColor('yellow')
            yl.setAlpha(100)
            lc.setPen(QPen(yl))
            lc.setBrush(QBrush(yl))
            lc.setZValue(-50)
            cont.lc = lc
            em = QGraphicsPixmapItem(QPixmap(self.api.icons['pink']), cont)
            em.setZValue(50)
            em.setOffset(-10, -10)
            self.scene.addItem(cont)
            self.connect(ai, SIGNAL('moved'), self.moveEm)
            self.stream.addEvent(ai.init)

    def initWorld(self):
        proto = QPolygonF([QPointF(0, 0), QPointF(0, 50), QPointF(50, 50), QPointF(50, 0)])
        for i in range(0, 5):
            b = Barrier(proto)
            b.translate(QPointF(randint(-300, 300), randint(-300, 300)))
            self.world.barriers.append(b)
            item = self.scene.addPolygon(b)
            item.setBrush(QBrush(QColor('black')))

    def moveEm(self, ai):
        ai.object.setPos(ai.pos)
        # ai.object.lc.setPos(ai.pos + QPointF(ai.lightr, ai.lightr))
        self.scene.update(self.scene.sceneRect())

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
