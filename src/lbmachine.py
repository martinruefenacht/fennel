from machine import Machine

class LatencyBandwidthMachine(Machine):
	def __init__(self, program, latency, bandwidth):
		super().__init__(program)	

		self.procs = [0] * program.size()

	def executeStartTask(self, task):
		self.procs[task.proc] = task.time

		return True, task.time

	def executeProxyTask(self, task):
		

	def executeSleepTask(self, task):
		 
