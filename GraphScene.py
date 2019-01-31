

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QTransform, QBrush
from PyQt5.QtCore import Qt, QLineF



class GraphicNode(QGraphicsEllipseItem):
	r = 40

	def __init__(self,point):
		super().__init__(point.x()-r,point.y()-r,2*r,2*r)
		self.setBrush(QBrush(Qt.light_blue))
		self.empty = True
		self.edge_graphics = []

	def center(self):
		return self.sceneBoundingRect().center()

class GraphicEdge(QGraphicLineItem):

	def __init__(self,line,src):
		super().__init__(line)
		self.setZValue(-100)
		self.source_node = src
		self.target_node = None

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

			item = self.itemAt(event.scenePos(), QTransform())

			if not item:
				self.addItem(GraphicNode(event.scenePos()))

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