import networkx as nx

# Program purely has directed acyclic graph and functions for usablility, does not record
# anything. Nor do the tasks change

class Program:
	def __init__(self):
		self.dag = nx.DiGraph()

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

	def getSuccessorTasks(self, node):
		return self.dag.successors_iter(node)
	
	def getStartTasks(self):
		# iterate all nodes
		for nid, degree in self.dag.in_degree_iter():
			# if no dependencies
			if degree == 0:
				# found start task
				yield self.dag.node[nid]['task']
