from machine import Machine

class LogPMachine(Machine):
	# LogP model parameters
	L = 1000
	o = 400
	g = 100

	def __init__(self, program):
		self.program = program

		# store cpu times
		self.procs = [0] * self.program.getSize()

		# procs are in machine as well
		# for drawing / analysis
		#self.record = {}

	#def getNetworkTime(self, source, target, size):
		# very simply topology implementation
		#sblade = source // 4
		#tblade = target // 4

		#if sblade == tblade:
		#	return Machine.alpha_p + Machine.beta * size

		#schassis = sblade // 16
		#tchassis = tblade // 16

		#if schassis == tchassis:
		#	return Machine.alpha_p + Machine.alpha_c + Machine.beta * size

		#sgroup = schassis // 6
		#tgroup = tchassis // 6

		#if sgroup == tgroup:
		#	return Machine.alpha_p + Machine.alpha_c + Machine.alpha_g + Machine.beta * size

		#return Machine.L + Machine.g_s + Machine.G * size
	
	def executeStartTask(self, task):
		self.procs[task.proc] = task.time
		
		return (True, task.time)

	def executeProxyTask(self, task):
		raise NotImplementedError	

	def executeSleepTask(self, task):
		if self.procs[task.proc] <= task.time:
			self.procs[task.proc] = task.time + task.delay
			
			return True, task.time + task.delay
		else:
			task.time = self.procs[task.proc]
			return False, None

	def executeComputeTask(self, task):
		if self.procs[task.proc] <= task.time:
			self.procs[task.proc] = task.time + task.delay
			
			return True, task.time + task.delay
		else:
			task.time = self.procs[task.proc]
			return False, None 

	def executePutTask(self, task):
		if self.procs[task.proc] <= task.time:
			local = task.time + LogPMachine.o
			
			self.procs[task.proc] = local

			remote = local + LogPMachine.g + LogPMachine.L

			return True, remote 
		else:
			# reinsert
			task.time = self.procs[task.proc]
			return False, None

