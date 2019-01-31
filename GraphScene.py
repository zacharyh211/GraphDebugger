

import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem, QGraphicsLineItem
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap, QTransform, QBrush
from PyQt5.QtCore import Qt, QLineF



class GraphicNode(QGraphicsEllipseItem):
	default_radius = 20

	def __init__(self,point):
		r = GraphicNode.default_radius
		super().__init__(point.x()-r,point.y()-r,2*r,2*r)
		self.setBrush(QBrush(Qt.cyan))
		self.empty = True
		self.edge_graphics = []

	def center(self):
		return self.sceneBoundingRect().center()

class GraphicEdge(QGraphicsLineItem):

	def __init__(self,src,line=None):
		super().__init__(line if line else QLineF(src.center(), src.center()))
		self.setZValue(-100)
		self.source_node = src
		src.edge_graphics.append(self)
		self.target_node = None

	def update_target(self, targ):
		if type(targ) == GraphicNode:
			self.target_node = targ
			targ.edge_graphics.append(self)
			self.setLine(QLineF(self.line().p1(), targ.center()))
		else:
			self.setLine(QLineF(self.line().p1(), targ.scenePos()))


class GraphScene(QGraphicsScene):

	def __init__(self):
		super().__init__()

		self.setSceneRect(0,0,1000,500)
		self.editing = True
		self.current_line = None
		self.left_start = True

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
			item = self.itemAt(event.scenePos(), QTransform())

			if not item:
				self.addItem(GraphicNode(event.scenePos()))
			elif type(item) == GraphicNode:
				if not self.current_line:
					self.current_line = GraphicEdge(item)
					self.addItem(self.current_line)
					self.left_start = False
				elif self.left_start:
					self.current_line.update_target(item)
					self.current_line = None

	def mouseMoveEvent(self, event):
		if self.editing:
			if self.current_line:
				self.current_line.update_target(event)
				if self.itemAt(event.scenePos(), QTransform()) != self.current_line.source_node:
					self.left_start = True


if __name__ == '__main__':
	app = QApplication(sys.argv)
	view = QGraphicsView()
	view.setMouseTracking(True)
	ex = GraphScene()
	view.setScene(ex)
	view.show()

	sys.exit(app.exec_())