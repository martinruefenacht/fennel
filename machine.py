from scipy.stats import betaprime

class Machine:
	alpha_r = 400
	alpha_p = 1600
	beta = 10
	gamma = 10
	def __init__(self, program):
		#self.size = program.getSize()
		self.size = 0
		for nid, deg in program.in_degree_iter():
			if deg == 0:
				self.size += 1

		# store cpu times
		self.procs = [0] * self.size

		# topology will need to be in here
		# a-b 1us, a-c 2us, c-d 1us
		# weighted all-to-all network

		# network congestion would require switch based simulation
		# with topology network

		# nic congestion, we need to treat the nic seperately similarly to LogP
		
		self.dependencies = {}
		self.dtimes = {}

		# for drawing / analysis
		self.record = {}

	def getRankTime(self, rank):
		return self.procs[rank]

	def setRankTime(self, rank, time):
		self.procs[rank] = time

	def markComplete(self, program, nid, time):
		successors = []

		for successor in program.successors_iter(nid):
			# increment completed dependencies for successor
			if successor in self.dependencies:
				self.dependencies[successor] += 1
			else:
				self.dependencies[successor] = 1

			# forward task to last dependency
			if successor in self.dtimes:
				self.dtimes[successor] = max(self.dtimes[successor], time)
			else:
				self.dtimes[successor] = time

			# check for completion
			if self.dependencies[successor] == program.in_degree(successor):
				successors.append((self.dtimes[successor], successor))

		return successors

	def getHostNoise(self, duration):
		return 0

	def getNetworkNoise(self, duration):
		return 0
