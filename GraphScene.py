

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from enum import Enum

import math
import json


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

	def __init__(self, nodes = None, edges = None, labels = None):
		self.edges = edges if edges else list()
		self.nodes = nodes if nodes else list()
		self.labels = labels if labels else dict()

	def write_graph(self, file):
		with open(file, 'w') as out:
			json.dump({'edges':[x.as_dict() for x in self.edges], 
					   'nodes':[x.as_dict() for x in self.nodes],
					   'labels':{s:id(n) for s,n in self.labels.items()}},out)

	def write_graph_to_json(self):
		return {'edges':[x.as_dict() for x in self.edges], 
				'nodes':[x.as_dict() for x in self.nodes],
				'labels':{s:id(n) for s,n in self.labels.items()}}

	def add_edge(self, e):
		self.edges.append(e)

	def remove_edge(self, e):
		self.edges.remove(e)

	def add_node(self, n):
		self.nodes.append(n)

	def remove_node(self, n):
		self.nodes.remove(n)
		self.labels = {key:value for key,value in self.labels.items() if value != n}

	def create_label(self, n, label):
		self.labels[label] = n
		n.label = label

	def read_graph(file):

		with open(file) as json_file:
			return Graph.read_graph_from_json(json.load(json_file))

	def read_graph_from_json(data):
		nodes = {}
		edges = {}
		labels = {}

		for n in data['nodes']:
			nodes[n['id']] = Node.from_dict(n)

		for e in data['edges']:
			tmp = edges[e['id']] = Edge.from_dict(e, nodes)
			s = tmp.src
			t = tmp.targ

			s.out.append(tmp)
			t.inc.append(tmp)
			s.adj.append(t)
			t.adj.append(s)

		for l,n in data['labels'].items():
			labels[l] = nodes[n]
			nodes[n].label = l

		return Graph(list(nodes.values()), list(edges.values()), labels)



class Edge:

	def __init__(self, src, targ, weight = -1):
		self.src = src
		self.targ = targ
		self.weight = weight
		self.flow = 0
		self.color = Color.BLACK
		self.graphic = GraphicEdge(self)

	def as_dict(self):

		d = {}

		d['id'] = id(self)
		d['src'] = id(self.src)
		d['targ'] = id(self.targ)
		d['weight'] = self.weight
		d['flow'] = self.flow
		d['color'] = self.color.value
		d['x1'] = self.graphic.line().p1().x()
		d['y1'] = self.graphic.line().p1().y()
		d['x2'] = self.graphic.line().p2().x()
		d['y2'] = self.graphic.line().p2().y()

		return d

	def from_dict(d, nodes):

		e = Edge(nodes[d['src']], nodes[d['targ']], d['weight'])
		return e

	@property
	def weight(self):
		return self._weight

	@weight.setter
	def weight(self, value):
		self._weight = value
		if hasattr(self, 'graphic'):
			self.graphic.update_label()

	@property
	def flow(self):
		return self._flow

	@flow.setter
	def flow(self, value):
		self._flow = value
		if hasattr(self, 'graphic'):
			self.graphic.update_label()

	def __lt__(self,other):
		return self.weight < other.weight

	def __gt__(self,other):
		return self.weight > other.weight

	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, value):
		self._color = value
		if hasattr(self, 'graphic'):
			self.graphic.update()


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

		#draw tip if directed
		if self.scene().show_direction:
			arrow_height = 10
			arrow_width = 10
			unit = self.line().unitVector()
			unit.setLength(self.line().length() - self.edge.targ.graphic.boundingRect().height()//2)
			points = []
			points.append(unit.p2())
			unit.setLength(unit.length() - arrow_height)
			base = unit.p2()
			unit = unit.normalVector().unitVector()
			unit.translate(base - unit.p1())
			unit.setLength(arrow_width//2)
			points.append(unit.p2())
			unit.setAngle(unit.angle() + 180)
			points.append(unit.p2())

			painter.setBrush(color_to_qt[self.edge.color])
			painter.drawPolygon(QPolygonF(points))


	def shape(self):
		path = super().shape()
		stroker = QPainterPathStroker()
		stroker.setWidth(15)
		return stroker.createStroke(path)

	def update_label(self):
		w = self.edge.weight
		f = self.edge.flow

		midpt = self.line().center()
		ang = (self.line().angle() + 90) % 360
		x,y = midpt.x(), midpt.y()

		if not self.edge_label:
			self.edge_label = QGraphicsTextItem('')
			self.scene().addItem(self.edge_label)

		if self.scene().show_flow and self.scene().show_weight:
			self.edge_label.setPlainText('{:g}/{:g}'.format(f if f is not None else math.nan,w if w is not None else math.nan))
		elif self.scene().show_weight:
			self.edge_label.setPlainText('{:g}'.format(w if w is not None else math.nan))
		elif self.scene().show_flow:
			self.edge_label.setPlainText('{:g}'.format(f if f is not None else math.nan))
		else:
			self.edge_label.setPlainText('')
		d = GraphicEdge.label_distance

		if ang >= 180:
			ang -= 180

		x += d * (math.cos(math.radians(ang)))
		y -= d * (math.sin(math.radians(ang)))

		x = x - self.edge_label.boundingRect().width() / 2
		y = y - self.edge_label.boundingRect().height() / 2

		self.edge_label.setPos(x,y)

class Node:

	def __init__(self,point):

		self.out = []
		self.inc = []
		self.adj = []
		self.label = ''
		self._color = Color.CYAN
		self.graphic = GraphicNode(self,point)

	def as_dict(self):

		d = {}

		d['id'] = id(self)
		d['out'] = [id(t) for t in self.out]
		d['inc'] = [id(t) for t in self.inc]
		d['adj'] = [id(t) for t in self.adj]
		d['color'] = self.color.value
		d['label'] = self.label
		d['x'] = self.graphic.center().x()
		d['y'] = self.graphic.center().y()
		d['r'] = self.graphic.boundingRect().height()//2

		return d

	def from_dict(d):
		n = Node(QPoint(d['x'], d['y']))
		#TODO: read color?
		return n

	def remove(self, e):
		if e.src == self:
			self.adj.remove(e.targ)
			self.out.remove(e)
		else:
			self.adj.remove(e.src)
			self.inc.remove(e)

	def _adj_edges(self):
		for e in self.inc:
			yield e,e.src
		for e in self.out:
			yield e,e.targ

	@property
	def adj_edges(self):
		return self._adj_edges()
	

	@property
	def color(self):
		return self._color

	@color.setter
	def color(self, value):
		self._color = value
		if hasattr(self, 'graphic'):
			self.graphic.update()

	@property
	def label(self):
		return self._label

	@label.setter
	def label(self, value):
		self._label = value
		if hasattr(self, 'graphic'):
			self.graphic.setToolTip(self._label)
	

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
		self.running = False
		self.current_line = None
		self.current_start = None
		self.graph = Graph()
		self.show_weight = False
		self.show_flow = False
		self.show_direction = False

	def set_show_weight(self, value):
		if value != self.show_weight:
			self.show_weight = value
			for e in self.graph.edges:
				e.graphic.update_label()

	def set_show_flow(self, value):
		if value != self.show_flow:
			self.show_flow = value
			for e in self.graph.edges:
				e.graphic.update_label()

	def set_show_direction(self, value):
		if  value != self.show_direction:
			self.show_direction = value
			for e in self.graph.edges:
				e.graphic.update()

	def set_graph(self, graph):
		self.clear()

		self.graph = graph

		for n in graph.nodes:
			self.addItem(n.graphic)
		for e in graph.edges:
			self.addItem(e.graphic)

	def set_graph_from_json(self, data):
		self.clear()

		self.graph = Graph.read_graph_from_json(data)

		for n in self.graph.nodes:
			self.addItem(n.graphic)
		for e in self.graph.edges:
			self.addItem(e.graphic)
			e.graphic.update_label()

	def get_graph(self):
		return self.graph

	def mouseDoubleClickEvent(self, event):
		self.mousePressEvent(event)

	def mousePressEvent(self, event):
		super().mousePressEvent(event)
		if not self.running:
			if event.button() == Qt.LeftButton:
				item = self.itemAt(event.scenePos(), QTransform())

				if not item:
					self.put_node(event.scenePos())
				elif type(item) == GraphicNode:
					if not self.current_line:
						self.current_line = QGraphicsLineItem(QLineF(item.center(), item.center()))
						self.current_line.setZValue(-100)
						self.current_start = item
						self.addItem(self.current_line)

	def mouseReleaseEvent(self,event):
		super().mouseReleaseEvent(event)
		if not self.running:
			if event.button() == Qt.LeftButton:
				item = self.itemAt(event.scenePos(), QTransform())
				if (not item or type(item) != GraphicNode) and self.current_line:
					self.removeItem(self.current_line)
					self.current_line = None
					self.current_start = None
				elif item != self.current_start and self.current_start:
					self.removeItem(self.current_line)

					self.put_edge(self.current_start, item)
					self.current_line = None
					self.current_start = None

	def mouseMoveEvent(self, event):
		if not self.running:
			if self.current_line:
				self.current_line.setLine(QLineF(self.current_line.line().p1(), event.scenePos()))

	def contextMenuEvent(self, event):

		item = self.itemAt(event.scenePos(), QTransform())

		if type(item) == GraphicEdge:
			menu = QMenu()

			set_weight = QAction('Set Edge Weight')
			set_weight.triggered.connect(lambda : self.set_edge_weight(item.edge))

			flip_edge = QAction('Flip Edge Direction')
			flip_edge.triggered.connect(lambda : self.flip_graphic_edge(item))

			remove_edge = QAction('Remove Edge')
			remove_edge.triggered.connect(lambda : self.remove_graphic_edge(item))

			menu.addAction(set_weight)
			menu.addAction(flip_edge)
			menu.addAction(remove_edge)
			menu.exec(QCursor.pos())

		elif type(item) == GraphicNode:
			menu = QMenu()

			label_node = QAction('Label Node')
			label_node.triggered.connect(lambda : self.label_graphic_node(item))

			remove_node = QAction('Remove Node')
			remove_node.triggered.connect(lambda : self.remove_graphic_node(item))

			menu.addAction(label_node)
			menu.addAction(remove_node)
			menu.exec(QCursor.pos())



	def put_node(self,pos):
		u = Node(pos)
		self.graph.add_node(u)
		self.addItem(u.graphic)

	def put_edge(self, u, v, w = None):
		u = u.node
		v = v.node

		if v in u.adj or u == v:
			return

		e = Edge(u,v,w)
		u.out.append(e)
		v.inc.append(e)
		u.adj.append(v)
		v.adj.append(u)
		self.graph.add_edge(e)
		self.addItem(e.graphic)

		if w is None and self.show_weight:
			self.set_edge_weight(e)

	def set_edge_weight(self, e):
		value, ok_pressed = QInputDialog.getDouble(None, "Input Weight", "Weight=")
		e.weight = value

	def remove_graphic_edge(self, e):
		self.removeItem(e)
		if e.edge_label:
			self.removeItem(e.edge_label)
		e = e.edge
		e.src.remove(e)
		e.targ.remove(e)
		self.graph.remove_edge(e)

	def remove_graphic_node(self, n):
		self.removeItem(n)
		n = n.node
		for e in n.out:
			self.remove_graphic_edge(e.graphic)
		for e in n.inc.copy():
			self.remove_graphic_edge(e.graphic)
		self.graph.remove_node(n)

	def flip_graphic_edge(self, e):
		edge = e.edge
		edge.src.out.remove(edge)
		edge.targ.inc.remove(edge)
		edge.src.inc.append(edge)
		edge.targ.out.append(edge)
		edge.src, edge.targ = edge.targ, edge.src
		e.update()

	def label_graphic_node(self,n):
		value, ok_pressed = QInputDialog.getText(None, "Input Label", "Label=")
		if not ok_pressed:
			return
		self.graph.create_label(n.node,value)



		


