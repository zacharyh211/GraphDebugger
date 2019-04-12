

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enum import Enum

import math


class Color(Enum):

	RED = 1
	BLACK = 2
	CYAN = 3
	BLUE = 4
	GRAY = 5
	WHITE = 6

color_to_qt = {
		Color.RED : Qt.red,
		Color.BLACK : Qt.black,
		Color.CYAN : Qt.cyan,
		Color.BLUE : Qt.blue,
		Color.GRAY : Qt.gray,
		Color.WHITE : Qt.white
	}

class Graph:

	def __init__(self, nodes = None, edges = None):
		self.edges = edges if edges else list()
		self.nodes = nodes if nodes else list()


class Edge:

	def __init__(self, src, targ, weight = None):
		self.src = src
		self.targ = targ
		self.weight = weight
		self.flow = 0
		self.color = Color.BLACK
		self.graphic = GraphicEdge(self)

class GraphicEdge(QGraphicsLineItem):

	label_distance = 15

	def __init__(self, edge):
		super().__init__(QLineF(edge.src.graphic.center(), edge.targ.graphic.center()))
		self.setZValue(-100)
		self.edge = edge
		self.edge_label = None

	def paint(self, painter, option, widget):
		super().setLine(QLineF(self.edge.src.graphic.center(), self.edge.targ.graphic.center()))
		self.setPen(QPen(color_to_qt[self.edge.color]))
		super().paint(painter, option, widget)

class Node:

	def __init__(self,point):

		self.out = []
		self.inc = []
		self.adj = []
		self._color = Color.CYAN
		self.graphic = GraphicNode(self,point)


	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, value):
		self._color = value
		self.graphic.update()

class GraphicNode(QGraphicsEllipseItem):
	default_radius = 18

	def __init__(self,node,point):
		r = GraphicNode.default_radius
		super().__init__(point.x()-r,point.y()-r,2*r,2*r)
		self.node = node

		self.setBrush(QBrush(color_to_qt[self.node.color]))

	def center(self):
		return self.sceneBoundingRect().center()

	def paint(self, painter, option, widget):
		self.setBrush(QBrush(color_to_qt[self.node.color]))
		super().paint(painter, option, widget)



class GraphScene(QGraphicsScene):

	def __init__(self):
		super().__init__()
		gui = self
		self.setSceneRect(0,0,500,500)
		self.editing = True
		self.current_line = None
		self.current_start = None

		self.nodes = []
		self.edges = []

	def get_graph(self):
		return Graph(self.nodes, self.edges)

	def mouseDoubleClickEvent(self, event):
		self.mousePressEvent(event)

	def mousePressEvent(self, event):
		if self.editing:
			if event.buttons() == Qt.LeftButton:
				item = self.itemAt(event.scenePos(), QTransform())

				if not item:
					self.put_node(event.scenePos())
				elif type(item) == GraphicNode:
					if not self.current_line:
						self.current_line = QGraphicsLineItem(QLineF(event.scenePos(), event.scenePos()))
						self.current_line.setZValue(-100)
						self.current_start = item
						self.addItem(self.current_line)

	def mouseReleaseEvent(self,event):
		if self.editing:
			if event.button() == Qt.LeftButton:
				item = self.itemAt(event.scenePos(), QTransform())
				if not item or type(item) != GraphicNode:
					self.removeItem(self.current_line)
					self.current_line = None
					self.current_start = None
				elif item != self.current_start and self.current_start:
					self.removeItem(self.current_line)
					self.put_edge(self.current_start, item)
					self.current_line = None
					self.current_start = None

	def mouseMoveEvent(self, event):
		if self.editing:
			if self.current_line:
				self.current_line.setLine(QLineF(self.current_line.line().p1(), event.scenePos()))

	def put_node(self,pos):
		u = Node(pos)
		self.nodes.append(u)
		self.addItem(u.graphic)

	def put_edge(self, u, v):
		u = u.node
		v = v.node
		e = Edge(u,v)
		u.out.append(e)
		v.inc.append(e)
		u.adj.append(v)
		v.adj.append(u)
		self.edges.append(e)
		self.addItem(e.graphic)
		self.add_edge_weight(e)

	def add_edge_weight(self, e):

		#TODO: Make value -> edge weight. Then have paint get the value from logical edge

		value, ok_pressed = QInputDialog.getDouble(None, "Input Weight", "Weight=")

		if int(value) == value:
			value = int(value)

		e.weight = value
		e = e.graphic

		midpt = e.line().center()
		ang = (e.line().angle() + 90) % 360
		x,y = midpt.x(), midpt.y()
		label = QGraphicsTextItem(str(value))
		d = GraphicEdge.label_distance

		if ang >= 180:
			ang -= 180

		x += d * (math.cos(math.radians(ang)))
		y -= d * (math.sin(math.radians(ang)))

		x = x - label.boundingRect().width() / 2
		y = y - label.boundingRect().height() / 2

		e.edge_label = label
		self.addItem(label)
		label.setPos(x,y)


