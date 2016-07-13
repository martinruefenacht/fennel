from machine import Machine
from visual import Visual
from tasks import *

class LogPMachine(Machine):
	# LogP model parameters
	L = 1000
	o = 400
	g = 100

	def __init__(self, program):
		super().__init__(program)

		# store cpu times
		self.procs = [0] * self.program.getSize()
		self.nic_sends = [0] * self.program.getSize()
		self.nic_recvs = [0] * self.program.getSize()

		self.host_noise = None
		self.network_noise = None

		self.task_handlers[StartTask] = self.executeStartTask
		self.task_handlers[ProxyTask] = self.executeProxyTask
		self.task_handlers[SleepTask] = self.executeSleepTask
		self.task_handlers[ComputeTask] = self.executeComputeTask
		self.task_handlers[PutTask] = self.executePutTask
		self.task_handlers[MsgTask] = self.executeMsgTask
	
	def getMaximumTime(self):
		return max(max(self.procs), max(self.nic_sends), max(self.nic_recvs))

	def executeStartTask(self, time, task):
		# check if cpu is available
		if self.procs[task.proc] > time:
			return [(self.procs[task.proc], task)]
	
		# no noise
		
		# skew entry
		self.procs[task.proc] = time + task.skew

		# draw
		self.drawStart(task, time)

		return self.completeTask(task, time + task.skew)

	def executeProxyTask(self, time, task):
		# forward process -> task finish
		self.procs[task.proc] = time

		# no noise

		# no visual

		# dependencies execute immediate
		return self.completeTask(task, time)

	def executeSleepTask(self, time, task):
		if self.procs[task.proc] <= time:
			# forward process -> task finish
			self.procs[task.proc] = time + task.delay

			# TODO noise
			noise = 0

			# visual
			self.drawSleep(task, time, noise)

			return self.completeTask(task, time+task.delay)
		else:
			return [(self.procs[task.proc], task)]

	def executeComputeTask(self, time, task):
		if self.procs[task.proc] <= time:
			# TODO noise
			noise = 0
			
			# visual
			self.drawCompute(task, time, noise)

			# forward process -> task finish
			self.procs[task.proc] = time + task.delay + noise

			return self.completeTask(task, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def executePutTask(self, time, task):
		available = max(self.procs[task.proc], self.nic_sends[task.proc])
		if available > time:
			return [(available, task)]
			
		# TODO noise
		noise_cpu = 0
		noise_nic = 0

		self.procs[task.proc] = time + LogPMachine.o + noise_cpu
		self.nic_sends[task.proc] = time + LogPMachine.g + noise_nic

		# visual
		self.drawPut(task, time, noise_cpu, noise_nic)

		start = time + LogPMachine.o + noise_cpu
		travel = time + LogPMachine.o + noise_cpu + LogPMachine.L
		msg = MsgTask(task, start, travel)
		
		return [(travel, msg)]	

	def executeMsgTask(self, time, task):
		available = self.nic_recvs[task.target]

		if available > time:
			return [(available, task)]
			
		# noise
		# TODO
		noise_nic = 0

		self.nic_recvs[task.target] = time + LogPMachine.g + noise_nic

		# visual
		self.drawMsg(task, time, noise_nic)

		# resolve put task dependencies
		return self.completeTask(task.puttask, time + LogPMachine.g + noise_nic)

	def drawStart(self, task, time):
		if self.context is not None:
			start_height = self.context.start_height
			start_radius = self.context.start_radius

			self.context.drawVLine(task.proc, time, start_height, start_height, 'std')
			self.context.drawCircle(task.proc, time, -start_height, start_radius)

	def drawSleep(self, task, time, noise):
		if self.context is not None:
			self.context.drawHLine(task.proc, time, task.delay, -self.context.sleep_height, 'std')	
	
	def drawCompute(self, task, time, noise):
		if self.context is not None:
			self.context.drawRectangle(task.proc, time, task.delay, Visual.compute_base, Visual.compute_height, 'std')

			if self.host_noise is not None:
				self.context.drawRectangle(task.proc, time+task.delay, noise, -self.context.compute_height/2, self.context.compute_height, 'err')


	def drawPut(self, task, time, noise_cpu, noise_nic):
		# check for visual context
		if self.context:
			side = 1 if task.proc < task.target else -1
			
			# draw put msg
			# cpu
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side, 'std')
			self.context.drawHLine(task.proc, time, LogPMachine.o, Visual.put_height*side, 'std')

			# nic
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side/2, 'std')
			self.context.drawHLine(task.proc, time, LogPMachine.g, Visual.put_height*side/2, 'std')

			# draw noise
			#if noise != 0:
			#	self.context.drawHLine(task.target, arrival, noise, -Visual.put_height*side, 'err')	
			#	self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_height*side, 'err')

	def drawMsg(self, task, time, noise_nic):
		if self.context:
			side = -1 if task.proc < task.target else 1

			# draw slant L line
			self.context.drawSLine(task.proc, task.start, -side*Visual.put_height, task.target, task.arrival, 'std')
			
			self.context.drawVLine(task.target, task.arrival, Visual.put_base, Visual.put_height*side, 'blu')
			self.context.drawVLine(task.target, time+LogPMachine.g+noise_nic, Visual.put_base, Visual.put_height*side, 'std')
			self.context.drawHLine(task.target, time, LogPMachine.g+noise_nic, Visual.put_height*side/2, 'std')
