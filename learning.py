

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QTransform, QBrush
from PyQt5.QtCore import Qt, QLineF

class GraphicNode(QGraphicsEllipseItem):

	def __init__(self,x,y,w,h):
		super().__init__(x,y,w,h)
		self.setBrush(QBrush(Qt.blue))
		self.empty = True

	def center(self):
		return self.sceneBoundingRect().center()

class GraphScene(QGraphicsScene):

	def _init_ui(self):
		self.setSceneRect(0,0,1000,500)

	def __init__(self):
		super().__init__()
		self._init_ui()
		self.nodes = []
		self.current_line = None
		self.inside_start = False

	def keyReleaseEvent(self, event):

		if event.key() == Qt.Key_Q:

			if self.current_line:
				self.removeItem(self.current_line)
				self.current_line = None
				self.inside_start = False

	def mousePressEvent(self, event):
		item = self.itemAt(event.scenePos(), QTransform())

		if not item:
			pt = event.scenePos()
			self.addItem(GraphicNode(pt.x() - 25, pt.y() - 25, 50, 50))
		elif type(item) == GraphicNode:
			if self.current_line:
				ln = self.current_line.line()
				self.current_line.setLine(QLineF(ln.p1(), item.center()))
				self.start = None
				self.current_line = None

			else:
				self.current_line = QGraphicsLineItem(QLineF(item.center(),item.center()))
				self.addItem(self.current_line)
				self.start = item
				self.inside_start = True
				self.current_line.setZValue(-1)
		else:
			return QGraphicsScene.mousePressEvent(self,event)

	def mouseReleaseEvent(self, event):
		item = self.itemAt(event.scenePos(), QTransform())

		if not self.inside_start and type(item) == GraphicNode and self.current_line:
			ln = self.current_line.line()
			self.current_line.setLine(QLineF(ln.p1(), item.center()))
			self.current_line = None
			self.start = None

	def mouseMoveEvent(self, event):

		if self.current_line:
			ln = self.current_line.line()
			self.current_line.setLine(QLineF(ln.p1(), event.scenePos()))

		if self.inside_start and self.itemAt(event.scenePos(), QTransform()) != self.start:
			self.inside_start = False

if __name__ == '__main__':
	
	app = QApplication(sys.argv)
	view = QGraphicsView()
	view.setMouseTracking(True)
	view.setRenderHint(QPainter.Antialiasing)
	ex = GraphScene()
	view.setScene(ex)
	view.show()

	sys.exit(app.exec_())
