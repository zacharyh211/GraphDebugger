
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from GraphScene import GraphicEdge, GraphicNode
from enum import Enum


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

class Graph(QObject):

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

	def get_node(self,label=None):
		if not label or label not in self.labels:
			return self.nodes[0] if len(self.nodes) > 0 else None
		return self.labels[label]




class Edge(QObject):

	label_changed = pyqtSignal(int, name='labelChanged')

	def __init__(self, src, targ, weight = -1):
		self.src = src
		self.targ = targ
		self.weight = weight
		self.flow = 0
		self.color = Color.BLACK
		self.graphic = GraphicEdge(self)
		self.label_changed.connect(self.graphic.update_label)

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


class Node(QObject):

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
			self.adj = [v for v in self.adj if v != e.targ]
			self.out.remove(e)
		else:
			self.adj = [v for v in self.adj if v != e.src]
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
