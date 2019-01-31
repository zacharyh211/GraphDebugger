

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

class GraphScene(QGraphicsScene):

	def __init__(self):
		super().__init__()

		self.setSceneRect(0,0,1000,500)
		self.editing = True
		self.nodes = []

	def keyReleaseEvent(self, event):
		print('keypress')
		if self.editing:
			pass

	def mouseReleaseEvent(self, event):
		print('unclicked')
		if self.editing:
			pass

	def mousePressEvent(self, event):
		print('clicked')
		if self.editing:
			pass

	def mouseMoveEvent(self, event):
		print('moving')
		if self.editing:
			pass

if __name__ == '__main__':
	app = QApplication(sys.argv)
	view = QGraphicsView()
	view.setMouseTracking(True)
	ex = GraphScene()
	view.setScene(ex)
	view.show()

	sys.exit(app.exec_())