from scipy.stats import betaprime

class Machine:
	alpha_r = 300
	alpha_p = 700
	alpha_c = 400 # cost of targetting a different chassis
	alpha_g = 500

	beta = 12.5
	gamma = 12.5

	def __init__(self, program, recording=False):
		self.recording = recording
	
		#self.size = program.getSize()
		self.size = 0
		for nid, deg in program.in_degree_iter():
			if deg == 0:
				self.size += 1

		# store cpu times
		self.procs = [0] * self.size

		# dependency counters
		self.dependencies = {}
		# dependency arrivals
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

	def getHostNoise(self, time, duration):
		return 0

	def getNetworkNoise(self, time, duration):
		return 0

	def getNetworkTime(self, source, target, size):
		sblade = source // 4
		tblade = target // 4

		if sblade == tblade:
			return Machine.alpha_p + Machine.beta * size

		schassis = sblade // 16
		tchassis = tblade // 16

		if schassis == tchassis:
			return Machine.alpha_p + Machine.alpha_c + Machine.beta * size

		sgroup = schassis // 6
		tgroup = tchassis // 6

		if sgroup == tgroup:
			return Machine.alpha_p + Machine.alpha_c + Machine.alpha_g + Machine.beta * size
	
	def recordTask(self, node, record):
		self.record[node] = record

class NoisyMachine(Machine):
	def getHostNoise(self, time, duration):
		#noise = betaprime.rvs(3, 2, scale=10)))
		
		noise = betaprime.rvs(3, 2, scale=duration/20)
	
		return int(round(noise))

	def getNetworkNoise(self, time, duration):
		#noise = betaprime.rvs(3, 2, scale=20)
		noise = betaprime.rvs(3, 2, scale=duration/25)
		
		return int(round(noise))


