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
		self.nics = [0] * self.program.getSize()

		self.host_noise = None
		self.network_noise = None

	def executeStartTask(self, time, task):
		# check if cpu is available
		if self.procs[task.proc] <= time:
			# no noise
			
			# skew entry
			self.procs[task.proc] = time + task.skew

			# draw
			self.drawStart(task, time)

			return True, time + task.skew
		else:
			return False, time

	def executeProxyTask(self, time, task):
		# forward process -> task finish
		self.procs[task.proc] = time

		# no noise

		# no visual

		# dependencies execute immediate
		return True, time

	def executeSleepTask(self, time, task):
		if self.procs[task.proc] <= time:
			# forward process -> task finish
			self.procs[task.proc] = time + task.delay

			# TODO noise
			noise = 0

			# visual
			self.drawSleep(task, time, noise)

			return True, time + task.delay
		else:
			return False, self.procs[task.proc]

	def executeComputeTask(self, time, task):
		if self.procs[task.proc] <= time:
			# TODO noise
			noise = 0
			
			# visual
			self.drawCompute(task, time, noise)

			# forward process -> task finish
			self.proc[task.proc] = time + task.delay + noise

			return True, self.procs[task.proc]
		else:
			return False, self.procs[task.proc]

	def executePutTask(self, time, task):
		if max(self.procs[task.proc], self.nics[task.proc]) <= time:
			# TODO noise
			noise_cpu = 0
			noise_nic = 0

			# visual
			self.drawPut(task, time, noise_cpu, noise_nic)
	
			self.procs[task.proc] = time + LogPMachine.o + noise_cpu
			self.send_nic[task.proc] = time + LogPMachine.g + noise_nic
		else:
			return False, max(self.procs[task.proc], self.nics[task.proc])

	def drawStart(self, task, time):
		pass

	def drawSleep(self, task, time, noise):
		pass
	
	def drawCompute(self, task, time, noise):
		pass

	def drawPut(self, task, time, noise_cpu, noise_nic):
		pass
