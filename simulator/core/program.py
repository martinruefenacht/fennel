class Program:
	def __init__(self):
		self.edges_in = {}
		self.edges_out = {}
		self.metadata = {}

	def getTask(self, nid):
		return self.metadata[nid]

	def addNode(self, nid, task):
		self.metadata[nid] = task

	def addEdge(self, nidfrom, nidto):
		# insert into out edges
		if nidfrom not in self.edges_out:
			self.edges_out[nidfrom] = [nidto]
		else:
			self.edges_out[nidfrom].append(nidto)

		# doubly link
		if nidto not in self.edges_in:
			self.edges_in[nidto] = [nidfrom]
		else:
			self.edges_in[nidto].append(nidfrom)

	def getProcessCount(self):
		size = 0
		
		for nid, task in self.metadata.items():
			if task.__class__.__name__ == "StartTask":
				size += 1

		return size

	def getStartTasks(self):
		for nid, task in self.metadata.items():
			if task.__class__.__name__ == "StartTask":
				yield task

	def getStartNodes(self):
		for nid, task in self.metadata.items():
			if task.__class__.__name__ == "StartTask":
				yield nid

	def getSuccessors(self, nid):
		# end of process check
		if nid in self.edges_out:
			# dependent tasks
			for eid in self.edges_out[nid]:
				yield eid

	def getInDegree(self, nid):
		if nid in self.edges_in:
			return len(self.edges_in[nid])
		else:
			return 0

	def getOutDegree(self, nid):
		if nid in self.edges_out:
			return len(self.edges_out[nid])
		else:
			return 0

	def prt(self):
		print(self.edges_out)
		print(self.metadata)
		print(self.edges_in)
