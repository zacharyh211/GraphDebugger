


import GraphScene, EditDebugger
from GraphScene import Color




def add_back_edge(g):

	n = g.get_node()
	
	e = GraphScene.Edge(n.adj[0], n)
	



graph = EditDebugger.app.get_graph()

add_back_edge(graph)
pass