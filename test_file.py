

import GraphScene, EditDebugger
from GraphScene import Color


graph = EditDebugger.app.get_graph()

first = graph.nodes[0]

stk = [first]
first.color = Color.BLUE

while stk:
	cur = stk.pop()

	if cur.color == Color.BLACK:
		continue
	cur.color = Color.BLACK

	for n in cur.adj:
		if n.color != Color.BLACK:
			n.color = Color.BLUE
			stk.append(n)
