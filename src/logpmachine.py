from machine import Machine
from visual import Visual
from tasks import *

class LogPMachine(Machine):
	def __init__(self, program, latency, overhead, gap):
		super().__init__(program)

		# LogP model parameters
		self.latency = latency
		self.gap = gap
		self.overhead = overhead

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

		# special to this model
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
		# cpu available
		if self.procs[task.proc] > time:
			return [(self.procs[task.proc], task)]

		# nic available
		if self.nic_sends[task.proc] > (time + self.overhead):
			diff = self.nic_sends[task.proc] - time + self.overhead
			return [(self.procs[task.proc] + self.overhead + diff, task)]
		
		# all local resources available

		# TODO noise
		noise_cpu = 0
		noise_nic = 0

		self.procs[task.proc] = time + self.overhead + noise_cpu
		self.nic_sends[task.proc] = time + self.overhead + self.gap + noise_nic

		# visual
		self.drawPut(task, time, noise_cpu, noise_nic)

		start = time + self.overhead + noise_cpu
		travel = start + self.latency
		msg = MsgTask(task, start, travel)
		
		return [(travel, msg)]	

	def executeMsgTask(self, time, task):
		available = self.nic_recvs[task.target]

		if available > time:
			return [(available, task)]
			
		# noise
		# TODO
		noise_nic = 0

		self.nic_recvs[task.target] = time + self.gap + noise_nic

		# visual
		self.drawMsg(task, time, noise_nic)

		# resolve put task dependencies
		# put is finished when processing with NIC is done
		# ie msg in memory
		return self.completeTask(task.puttask, time + self.gap + noise_nic)

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
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side*3/4, 'std')
			self.context.drawHLine(task.proc, time, self.overhead, Visual.put_height*side*3/4, 'std')

			# nic
			self.context.drawVLine(task.proc, time+self.overhead, Visual.put_base, Visual.put_height*side, 'std')
			self.context.drawHLine(task.proc, time+self.overhead, self.gap, Visual.put_height*side, 'blu')

			
			# draw noise
			#if noise != 0:
			#	self.context.drawHLine(task.target, arrival, noise, -Visual.put_height*side, 'err')	
			#	self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_height*side, 'err')

	def drawMsg(self, task, time, noise_nic):
		if self.context:
			side = 1 if task.proc < task.target else -1

			# draw slant L line
			self.context.drawSLine(task.proc, task.start, Visual.put_height, task.target, task.arrival, 'std')
			
			self.context.drawVLine(task.target, task.arrival, Visual.put_base, Visual.put_height*-side, 'blu')
			self.context.drawVLine(task.target, time+self.gap+noise_nic, Visual.put_base, Visual.put_height*-side, 'std')
			self.context.drawHLine(task.target, time, self.gap+noise_nic, Visual.put_height*-side/2, 'std')

class LogPMachineSimplex(LogPMachine):
	def __init__(self, program, latency, overhead, gap):
		super().__init__(program, latency, overhead, gap)

		self.task_handlers[NICTask] = self.executeNICTask

	def executePutTask(self, time, task):
		# cpu available
		if self.procs[task.proc] > time:
			return [(self.procs[task.proc], task)]

		# nic available
		# WE DONT KNOW THIS!
		# NIC COULD ENCOUNTER RECV AT IDLE AND THEN NOT BE FREE
		#if self.nic_sends[task.proc] > (time + self.overhead):
	#		diff = self.nic_sends[task.proc] - time + self.overhead
	#		return [(self.procs[task.proc] + self.overhead + diff, task)]
		
		# all local resources available

		# TODO noise
		noise_cpu = 0

		self.procs[task.proc] = time + self.overhead + noise_cpu
		
		# WE DONT KNOW THAT NOTHING HAPPENS BEFORE THIS
		# THIS IS A BUG
		# CANT JUST FORWARD, NEED TO INSERT INTO QUEUE
		# WE DID THE HEAP BY TIME NIC WAS TIME + O
		#self.nic_sends[task.proc] = time + self.overhead + self.gap + noise_nic

		# visual
		self.drawPut(task, time, noise_cpu)

		nictask = NICTask(task)
				
		return [(time + self.overhead, nictask)]	

	def executeNICTask(self, time, task):
		available = self.nic_sends[task.proc]

		if available > time:
			# NIC TASK SHOULD NOT BE RESCHEDULABLE
			# THIS IS A PROBLEM
			return [(available, task)]

		# noise
		noise_nic = 0

		self.nic_sends[task.proc] = time + self.gap + noise_nic

		self.drawNIC(task, time, noise_nic)

		travel = time + self.latency
		msg = MsgTask(task.puttask, time, travel)

		return [(time, msg)]

	def executeMsgTask(self, time, task):
		available = self.nic_sends[task.target]

		if available > time:
			return [(available, task)]
			
		# noise
		# TODO
		noise_nic = 0

		self.nic_sends[task.target] = time + self.gap + noise_nic

		# visual
		self.drawMsg(task, time, noise_nic)

		# resolve put task dependencies
		# put is finished when processing with NIC is done
		# ie msg in memory
		return self.completeTask(task.puttask, time + self.gap + noise_nic)

	def drawNIC(self, task, time, noise_nic):
		if self.context:
			side = 1 if task.puttask.proc < task.puttask.target else -1

			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side, 'std')
			self.context.drawHLine(task.proc, time, self.gap, Visual.put_height*side/2, 'blu')

	def drawMsg(self, task, time, noise_nic):
		if self.context:
			side = 1 if task.proc < task.target else -1

			# draw slant L line
			self.context.drawSLine(task.proc, task.start, Visual.put_height, task.target, task.arrival, 'std')
			
			self.context.drawVLine(task.target, task.arrival, Visual.put_base, Visual.put_height*-side, 'blu')
			self.context.drawVLine(task.target, time+self.gap+noise_nic, Visual.put_base, Visual.put_height*-side, 'std')
			self.context.drawHLine(task.target, time, self.gap+noise_nic, Visual.put_height*-side, 'std')
			self.context.drawHLine(task.target, task.arrival, time-task.arrival, Visual.put_height*-side/4, 'std')

			self.context.drawVLine(task.target, time, Visual.put_base, Visual.put_height*-side, 'std')

	def drawPut(self, task, time, noise_cpu):
		# check for visual context
		if self.context:

			side = 1 if task.proc < task.target else -1
			
			# draw put msg
			# cpu
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side*3/4, 'std')
			self.context.drawHLine(task.proc, time, self.overhead, Visual.put_height*side*3/4, 'std')

			# draw noise
			#if noise != 0:
			#	self.context.drawHLine(task.target, arrival, noise, -Visual.put_height*side, 'err')	
			#	self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_height*side, 'err')

class LogGPMachine(LogPMachine):
	def __init__(self, program, latency, overhead, gap, longgap):
		super().__init__(program, latency, overhead, gap)

		# LogGP model parameter
		self.longgap = longgap
