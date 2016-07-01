import networkx as nx

class Program:
	def __init__(self):
		self.dag = nx.DiGraph()

		self.procs = [0] * size

	def getTask(nid):
		return self.dag.node[nid]['task']

	def addTask(name, task):
		self.dag.add_node(name, {'task':task, 'dependencies':0})

