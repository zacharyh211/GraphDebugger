

import GraphScene, EditDebugger
from GraphScene import Color
import heapq, math


def fordfulkerson(g):

	for e in g.edges:
		e.flow = 0

	s = g.get_node('source')
	t = g.get_node('target')

	path = []
	while get_path(g,s,t,path):
		residual_cap = min(e.weight - e.flow if forward else e.flow for forward,e in path)

		for forward,e in path:
			if forward:
				e.flow += residual_cap
			else:
				e.flow -= residual_cap
		path = []


def get_path(g,s,t,path):

	if s == t:
		return path

	for e in s.out:
		if e.weight > e.flow:
			path.append((True,e))
			p = get_path(g,e.targ, t, path)
			if p:
				return p
			path.pop()

	for e in s.inc:
		if e.flow > 0:
			path.append((False,e))
			p = get_path(g,e.src, t, path)
			if p:
				return p
			path.pop()

	return None



graph = EditDebugger.app.get_graph()
fordfulkerson(graph)
pass