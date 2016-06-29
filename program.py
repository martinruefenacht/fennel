import networkx as nx

class Program(nx.DiGraph):
	def __init__(self):
		self.add_node('p0is', {'task':StartTask(0)})     
		self.add_node('p0i1', {'task':PutTask(0, 1, 8)})
		self.add_node('p0i2', {'task':ComputeTask(0, 100)})
		self.add_node('p0ie', {'task':EndTask(0)})

		self.add_node('p1is', {'task':StartTask(1)}) 
		self.add_node('p1i1', {'task':PutTask(1, 0, 8)})
		self.add_node('p1i2', {'task':ComputeTask(1, 100)})
		self.add_node('p1ie', {'task':EndTask(1)})

		self.add_edge('p0is','p0i1')
		self.add_edge('p0is','p0i2')
		self.add_edge('p1i1','p0i2')
		self.add_edge('p0i2','p0ie')
		   
		self.add_edge('p1is','p1i1')
		self.add_edge('p1is','p1i2')
		self.add_edge('p0i1','p1i2')
		self.add_edge('p1i2','p1ie')	
