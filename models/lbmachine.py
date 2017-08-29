import fennel.core.machine as machine
import fennel.core.tasks as tasks

from fennel.visual.visualizer import Visual
#import math

class LBMachine(machine.Machine):
	def __init__(self, nodes, latency, bandwidth):
		super().__init__(nodes)

		# model parameters
		self.alpha = latency
		self.beta = bandwidth

		# process times
		self.procs = [0] * self.node_count
		self.maximum_time = 0

		# noise
		self.noise_record = {}
		self.host_noise = None
		self.network_noise = None

		# set supported tasks for LBMachine model
		self.task_handlers['StartTask'] = self.executeStartTask
		self.task_handlers['ProxyTask'] = self.executeProxyTask
		self.task_handlers['SleepTask'] = self.executeSleepTask
		self.task_handlers['ComputeTask'] = self.executeComputeTask
		self.task_handlers['PutTask'] = self.executePutTask

	def reset(self):
		super().reset()
		
		self.noise_record = {}
		self.maximum_time = 0

	def getMaximumTime(self):
		return max(self.procs)	

	def getHostNoise(self, duration):
		if self.host_noise:
			return self.host_noise.generate(duration)
		else:
			return 0

	def getNetworkNoise(self, duration):
		if self.network_noise:
			return self.network_noise.generate(duration)
		else:
			return 0

	
	def executeStartTask(self, time, program, task):
		# logic
		if self.procs[task.proc] <= time:
			# no noise

			# forward proc
			self.procs[task.proc] = time + task.skew

			# visual
			self.drawStart(time, task)

			# return list of dependencies which are fulfilled
			return self.completeTask(task, program, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def drawStart(self, time, task):
		if self.context is not None:
			start_height = self.context.start_height
			start_radius = self.context.start_radius

			self.context.drawVLine(task.proc, time, start_height, start_height, 'std')
			self.context.drawCircle(task.proc, time, -start_height, start_radius)

	def executeProxyTask(self, time, program, task):
		# logic
		self.procs[task.proc] = time

		# no noise

		# no visual

		#
		return self.completeTask(task, program, self.procs[task.proc])

	def executeSleepTask(self, time, program, task):
		# logic
		if self.procs[task.proc] <= time:
			# noise
			# TODO
			
			# forward proc
			self.procs[task.proc] = time + task.delay

			# visual
			self.drawSleepTask(time, task)

			#
			return self.completeTask(task, program, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def drawSleepTask(self, time, task):
		if self.context is not None:
			self.context.drawHLine(task.proc, time, task.delay, -self.context.sleep_height, 'std')	
		 
	def executeComputeTask(self, time, program, task):
		if self.procs[task.proc] <= time:
			# noise
			#noise = self.getHostNoise(task.delay)
			noise = 0
			#TODO

			# forward proc
			self.procs[task.proc] = time + task.delay + noise

			# visual 
			self.drawCompute(task, time, noise)
			
			return self.completeTask(task, program, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def drawCompute(self, task, time, noise):		
		if self.context is not None:
			self.context.drawRectangle(task.proc, time, task.delay, Visual.compute_base, Visual.compute_height, 'std')

			if self.host_noise is not None:
				self.context.drawRectangle(task.proc, time+task.delay, noise, -self.context.compute_height/2, self.context.compute_height, 'err')

	def executePutTask(self, time, program, task):
		# 
		if self.procs[task.proc] > time:
			# fail
			return [(self.procs[task.proc], task)]

		# put side
		put_time = self.alpha + self.beta * task.size
		noise_put = self.getNetworkNoise(put_time)
		arrival = time + put_time
		time_put = arrival + noise_put

		# draw put side
		self.drawPut(task, time, arrival, noise_put)

		# blocking put and put and same under LB machine

		# 
		self.procs[task.proc] = time_put
		self.maximum_time = max(self.maximum_time, time_put)

		
		return self.completeTask(task, program, time_put)

	def drawPut(self, task, time, arrival, noise):
		# check for visual context
		if self.context:
			side = 1 if task.proc < task.target else -1
			
			# draw put msg
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side, 'std')
			self.context.drawSLine(task.proc, time, Visual.put_height, task.target, arrival, 'std')
			self.context.drawVLine(task.target, arrival, Visual.put_base, Visual.put_height*-side, 'std')
		
			# draw noise
			if noise != 0:
				self.context.drawHLine(task.target, arrival, noise, -Visual.put_height*side, 'err')	
				self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_height*side, 'err')
			
class LBPMachine(LBMachine):
	def __init__(self, nodes, latency, bandwidth, pipelining):
		super().__init__(nodes, latency, bandwidth)

		self.kappa = pipelining
		self.network_lock = [0] * 40

	def getMaximumTime(self):
		return self.maximum_time

	def executePutTask(self, time, program, task):
		# 
		if self.procs[task.proc] > time:
			# fail
			# reinsert task at delayed time
			return [(self.procs[task.proc], task)]

		# pipeline
		pipe_time = self.kappa
		noise_pipe = self.getHostNoise(pipe_time)
		time_pipe = time + pipe_time + noise_pipe

		# XXX NETWORK LOCK quick and dirty
		if self.network_lock[time_pipe // 50]:
			return [(((time_pipe // 50) + 1) * 50, task)]
		self.network_lock[time_pipe // 50] = True

		# draw pipeline
		self.drawPipe(task, time, self.kappa, noise_pipe)

		# put side
		put_time = self.alpha + self.beta * task.size
		noise_put = self.getNetworkNoise(put_time)
		arrival = time_pipe + put_time
		time_put = arrival + noise_put

		# draw put side
		self.drawPut(task, time_pipe, arrival, noise_put)

		#
		if task.block:
			self.procs[task.proc] = time_put
		else:
			self.procs[task.proc] = time_pipe
		self.maximum_time = max(self.maximum_time, time_put)

		return self.completeTask(task, program, time_put)

	def drawPipe(self, task, time, delay, noise):
		#
		if self.context:
			side = 1 if task.proc < task.target else -1

			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_height*side, 'std')
			
			boxheight = Visual.put_height - Visual.put_offset
			offset = boxheight/2 + Visual.put_offset
			self.context.drawRectangle(task.proc, time, delay, offset*side, boxheight, 'std')
			
			if noise != 0:
				self.context.drawHLine(task.proc, time+delay, noise, Visual.put_height*side, 'err')

class LBPCMachine(LBPMachine):
	def __init__(self, nodes, latency, bandwidth, pipelining, congest):
		super().__init__(nodes, latency, bandwidth, pipelining)

		self.congestion = congest
		
		# initialize nic recving side "time"
		self.nic_recv = [0] * self.node_count

		self.task_handlers['MsgTask'] = self.executeMsgTask

	def getMaximumTime(self):
		return self.maximum_time

	def executePutTask(self, time, program, task):
		# 
		if self.procs[task.proc] > time:
			# fail
			# reinsert task at delayed time
			return [(self.procs[task.proc], task)]

		# pipeline
		pipe_time = self.kappa
		noise_pipe = self.getHostNoise(pipe_time)
		time_pipe = time + pipe_time + noise_pipe

		# draw pipeline
		self.drawPipe(task, time, self.kappa, noise_pipe)

		# put side
		put_time = self.alpha + self.beta * task.size
		noise_put = self.getNetworkNoise(put_time)
		arrival = time_pipe + put_time
		time_put = arrival + noise_put

		#return MsgTaskType?

		#if self.nic_recv[task.proc] > time_put:
			# reinsert recv

		# draw put side
		self.drawPut(task, time_pipe, arrival, noise_put)

		#
		#if task.block:
		#	self.procs[task.proc] = time_put
		#else:
		self.procs[task.proc] = time_pipe
		self.maximum_time = max(self.maximum_time, time_put)

		#self.completeTask(task, program, time_put)

		msgtask = tasks.MsgTask(task, time_pipe, time_put)

		return [(time_put, msgtask)]

	def executeMsgTask(self, time, program, task):
		#print(task.name, time, self.nic_recv[task.target])
		if self.nic_recv[task.target] > time:
			# reinsert
			return [(self.nic_recv[task.target], task)]

		self.nic_recv[task.target] = time + self.congestion # + noise

		self.drawRecv(task, time + self.congestion, 0)
		

		return self.completeTask(task.puttask, program, time + self.congestion)

	def drawRecv(self, task, time, noise):
		pass	
		# TODO
