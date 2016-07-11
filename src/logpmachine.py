from machine import Machine

class LogPMachine(Machine):
	# LogP model parameters
	L = 200
	o = 400
	g = 200

	def __init__(self, program):
		self.program = program

		# store cpu times
		self.procs = [0] * self.program.getSize()
		self.nic_send = [0] * self.program.getSize()
		self.nic_recv = [0] * self.program.getSize()

		self.host_noise = None
		self.network_noise = None

	def executeStartTask(self, task):
		raise NotImplementedError

	def executeProxyTask(self, task):
		raise NotImplementedError	

	def executeSleepTask(self, task):
		raise NotImplementedError

	def executeComputeTask(self, task):
		raise NotImplementedError	

	def executePutTask(self, task):
		raise NotImplementedError

#class LogGOPMachine(LogPMachine):
#	O = 0.1
#	G = 0.1
