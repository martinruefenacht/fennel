import networkx as nx

class Program:
	def __init__(self):
		self.dag = nx.DiGraph()

		self.procs = [0] * size

	def getTask(self, nid):
		return self.dag.node[nid]['task']

	def addTask(self, name, task):
		self.dag.add_node(name, {'task':task, 'dependencies':0})

	def getSize(self):
		size = 0
		
		for nid, deg in self.dag.in_degree_iter():
			if deg == 0:
				size += 1

		return size
	
	def findAllStartNodes(self):
		pass

