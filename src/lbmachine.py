from machine import Machine

class LBMachine(Machine):
	def __init__(self, program, latency, bandwidth):
		super().__init__(program)

		self.alpha = latency
		self.beta = bandwidth

		self.procs = [0] * program.getSize()

	def executeStartTask(self, task):
		self.procs[task.proc] = task.time

		return True, task.time

	def executeProxyTask(self, task):
		self.procs[task.proc] = task.time

		return True, task.time

	def executeSleepTask(self, task):
		if self.procs[task.proc] <= task.time:
			self.procs[task.proc] = task.time + task.delay	

			return True, self.procs[task.proc]
		else:
			task.time = self.procs[task.proc]
			return False, None
		 
	def executeComputeTask(self, task):
		if self.procs[task.proc] <= task.time:
			self.procs[task.proc] = task.time + task.delay
			
			return True, self.procs[task.proc]
		else:
			task.time = self.procs[task.proc]
			return False, None

	def executePutTask(self, task):
		if self.procs[task.proc] <= task.time:
			local = task.time + self.alpha
			remote = local + self.beta * task.size

			self.procs[task.proc] = local
			return True, remote
		else:
			task.time = self.procs[task.proc]
			return False, None

#class NoisyLBMachine(LBMachine):	

#class VisualLBMachine(LBMachine):

#class VisualNoisyLBMachine(LBMachine):
