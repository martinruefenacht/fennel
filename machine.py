class Machine:
	def __init__(self, program):
		#self.size = program.getSize()
		
		
		self.size = 0
		for nid, deg in program.in_degree_iter():
			if deg == 0:
				self.size += 1

		# store cpu times
		self.procs = [0] * self.size

		# topology will need to be in here
