#!/usr/bin/env python
# -*- coding: utf-8 -*-c
from __future__ import print_function, unicode_literals
import sys
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from winterstone.base import *
from loader import Loader
from base import AI, World, Stream, Barrier
from random import randint


class API(WinterAPI):
    """
        What ai can do with app (draw dots, get stats...)
    """
    def __init__(self, scene, world):
        WinterAPI.__init__(self)
        self.__scene = scene
        self.__world = world
        self.points = []
        self.pi = QGraphicsPolygonItem(scene=self.__scene)

    def drawPoint(self, x, y, color='red', r=2):
        # print(len(self.points))
        #if len(self.points) >= 50:
            # self.points[0].hide()
            # self.__scene.removeItem(self.points[0])
            #odd = self.points[0:len(self.points) - 50]
            #for p in odd:
                #p.hide()
                #self.points.remove(p)
                #self.__scene.removeItem(p)
        e = QGraphicsEllipseItem(
            QRectF(QPointF(x - r, y - r), QPointF(x + r, y + r)), parent=self.pi, scene=self.__scene
        )
        e.setPen(QPen(QColor(color)))
        e.setBrush(QBrush(QColor(color)))
        # self.__scene.addItem(e)
        self.points.append(e)
        return e

    def drawLine(self, x, y, x1, y1, color='blue'):
        l = QGraphicsLineItem(QLineF(QPointF(x, y), QPointF(x1, y1)), parent=self.pi, scene=self.__scene)
        l.setPen(QPen(QColor(color)))
#        self.__scene.addItem(l)
        return l

    def getStats(self, who, stat):  # remove who by personal apis
        return self.__world.stats[who][stat]

    def addStats(self, who, stat):  # remove who by personal apis
        if self.__world.stats[who]['skillpoints'] > 0:
            self.__world.stats[who]['skillpoints'] -= 1
            self.__world.stats[who][stat] += 1


class UI(QMainWindow):
    """
        Main class. UI + graphics
    """

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

    def start(self):  # Implement restart button with ai reloading
        self.scene.clear()
        self.drawDots()  # Coordinate helper
        self.loadAI()  # Get ais from plugins
        self.stream = Stream(self.ai)  # Main stream of events
        self.world = World(stream=self.stream)  # Main container of objects
        self.stream.start()
        self.world.ai = self.ai
        self.initWorld()  # Init barriers, and other stuff
        self.api = API(self.scene, self.world)  # TODO: remove singleton, make personal apis
        self.api.addIconsFolder('static')
        self.api.addIconsFolder('static/emblems')
        self.initAI()  # Create AI, place in World

    def initAI(self):  # Move not-gui logic to World
        for ai in self.ai:
            ai.world = World(ai, self.world)
            ###  # Start stats. Move to World
            self.world.stats[ai] = {
                'pos': QPointF(randint(-50, 50), randint(-50, 50)),
                'speed': 20,
                'skillpoints': 5,
                'hp': 50,
                'ac': 10,
                'light': 150,
                'light_angle': 90,
                'angle': 0
            }
            ###
            if ai.color == 'orange':
                self.world.stats[ai]['speed'] = 40
            ai.world.stream = self.stream
            ai.api = self.api
            ###  # Init start position and graphics logic
            cont = QGraphicsPolygonItem()
            cont.setPos(self.world.stats[ai]['pos'])  # Implement start areas
            ai.object = cont
            cont.ai = ai
            ###  # Draw light circle and color dot
            lc = QGraphicsEllipseItem(QRectF(QPointF(-ai.lightr, -ai.lightr), QSizeF(ai.lightr * 2, ai.lightr * 2)), cont)
            lc.setStartAngle((90 - self.world.stats[ai]['light_angle'] / 2) * 16)
            lc.setSpanAngle(self.world.stats[ai]['light_angle'] * 16)
            lc.setTransformOriginPoint(QPointF(0, 0))
            yl = QColor('yellow')
            yl.setAlpha(100)
            lc.setPen(QPen(yl))
            lc.setBrush(QBrush(yl))
            lc.setZValue(-50)
            cont.lc = lc
            em = QGraphicsPixmapItem(QPixmap(self.api.icons[ai.color]), cont)
            em.setZValue(50)
            em.setOffset(-10, -10)
            cont.em = em
            # ra = QGraphicsLineItem(QLineF(QPointF(0, 40), QPointF(0, 0)), cont)
            # cont.ra = ra
            self.scene.addItem(cont)
            self.connect(ai, SIGNAL('moved'), self.moveAI)
            self.stream.addEvent(ai.init)  # Start AI init method

    def initWorld(self):  # Move not-gui logic to World
        proto = QPolygonF([QPointF(0, 0), QPointF(0, 50), QPointF(50, 50), QPointF(50, 0)])
        for i in range(0, 5):
            b = Barrier(proto)
            b.translate(QPointF(randint(-300, 300), randint(-300, 300)))
            self.world.barriers.append(b)
            item = self.scene.addPolygon(b)
            item.setBrush(QBrush(QColor('black')))

    def moveAI(self, ai):  # Drow changed position
        ai.object.setPos(ai.pos)
        ai.object.lc.setRotation(ai.angle)
        # ai.object.ra.setRotation(ai.angle)
        self.scene.update(self.scene.sceneRect())

    def drawDots(self):  # Helper
        tl = QPoint(-300, -300)
        br = QPoint(300, 300)
        step = 20
        for x in range(tl.x(), br.x(), step):
            for y in range(tl.y(), br.y(), step):
                e = self.scene.addEllipse(QRectF(QPointF(x, y), QPointF(x + 0.5, y + 0.5)), QPen(QColor('#555')))
                e.setZValue(-60)

    def loadAI(self):  # Load ais files
        self.loader = Loader(AI, 'ai')
        self.ai = self.loader.modules


def main():
    qtapp = QApplication(sys.argv)
    win = UI()
    win.show()
    qtapp.exec_()
    win.stream.stop()
    win.stream.wait()


if __name__ == '__main__':
    main()
