# Graph Visual Debugger

A Python 3 debugging tool which provides a visual representation of graph algorithms written using the basic included object oriented graph library. Users can see node and edge colorings, edge weights, edge direction, flow values, and node labels during execution. Graphs are constructed within the interface and can be easily referenced within user scripts to request node and edge iterators or to request specific nodes by label. 


### Installing

Install using pip:

```
  $ pip install VisualGraphDebugger-zacharyh211
```

### Launching

Run from terminal:

```
  $ vgd
```
Or run with graph and/or script pre-loaded:

```
  $ vgd -g myGraph.json -s myScript.py
```

### Basic Usage of Graph module

Scripts must be written using the included Graph module to be compatible with this debugging tool. To retrieve the graph drawn on the UI, use the following:
```
  from Graph import Graph

  graph = Graph.get_graph()
```
Nodes and edges can be accessed by using graph.nodes and graph.edges, respectively.

#### Getting Neighbors

Connected edges and adjacent nodes can be accessed as follows:
```
node.inc # incoming edges
node.out # outgoing edges
node.adj_edges # all edges as an (edge,neighbor) tuple
node.adj # all connected nodes

edge.src # source node of this edge
edge.targ # target node of this edge
```

#### Node Properties

Each node has a color and a label. 

The color can be set to any value in the Color enum contained within the Graph module and will be reflected within the debugger.

The label can be set to any string and can be seen within the debugging canvas by hovering over the node. Additionally, labels can be set prior to running the current script and then be requested using:
```
graph.get_node('node label')
```

#### Edge Properties

Each edge has a color, weight, and flow amount.

The color can be set to any value in the Color enum contained within the Graph module and will be reflected within the debugger.

The weight and flow will be displayed alongside the edges in the form "{weight} / {flow}" when this options are toggled On.

### The Debugger

#### Creating Graphs

Graphs can either be imported using File > Import Graph or can be created manually. 

To begin creating a graph manually, simply click anywhere on the canvas to add a node. This node can be removed by right-clicking and selecting "Remove Node". This deletes the node and any connected edges.

To add edges to the graph, click on a source node and then click on a target node. If weights are toggled on, you will be prompted to set an Edge weight. Edge weights can be set or changed by right clicking them.

#### Debugging Scripts

Breakpoints can be set and turned off by double clicking in the text editor margin. 

Clicking "Run" will execute the script until reaching the first breakpoint. 

"Resume" will continue execution until the next breakpoint. 

"Step" will execute the next line on the indicator and pause execution until receiving another input.

"Skip" will execute the current line without tracing the next function call made.


