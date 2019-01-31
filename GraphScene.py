

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QTransform, QBrush
from PyQt5.QtCore import Qt, QLineF



class GraphicNode(QGraphicsEllipseItem):

	def __init__(self,x,y,w,h):
		super().__init__(x,y,w,h)
		self.setBrush(QBrush(Qt.light_blue))
		self.empty = True
		self.edge_graphics = []

	def center(self):
		return self.sceneBoundingRect().center()

