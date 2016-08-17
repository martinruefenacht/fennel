from machine import Machine
from scipy.stats import betaprime
from random import choice
import math


from tasks import *
from visual import Visual

class LBMachine(Machine):
	def __init__(self, program, latency, bandwidth):
		super().__init__(program)

		# model parameters
		self.alpha = latency
		self.beta = bandwidth

		# process times
		self.procs = [0] * program.getSize()
		self.maximum_time = 0

		# noise
		self.noise_record = {}
		self.host_noise = None
		self.network_noise = None

		self.task_handlers[StartTask] = self.executeStartTask
		self.task_handlers[ProxyTask] = self.executeProxyTask
		self.task_handlers[SleepTask] = self.executeSleepTask
		self.task_handlers[ComputeTask] = self.executeComputeTask
		self.task_handlers[PutTask] = self.executePutTask

	def reset(self):
		super().reset()
		
		self.noise_record = {}
		self.maximum_time = 0

		self.procs = [0] * self.program.getSize()

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

	
	def executeStartTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# no noise

			# forward proc
			self.procs[task.proc] = time + task.skew

			# visual
			self.drawStart(time, task)

			# return list of dependencies which are fulfilled
			return self.completeTask(task, self.procs[task.proc])
		else:
			return (time, task)

	def drawStart(self, time, task):
		if self.context is not None:
			start_height = self.context.start_height
			start_radius = self.context.start_radius

			self.context.drawVLine(task.proc, time, start_height, start_height, 'std')
			self.context.drawCircle(task.proc, time, -start_height, start_radius)

	def executeProxyTask(self, time, task):
		# logic
		self.procs[task.proc] = time

		# no noise

		# no visual

		#
		return self.completeTask(task, self.procs[task.proc])

	def executeSleepTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# noise
			# TODO
			
			# forward proc
			self.procs[task.proc] = time + task.delay

			# visual
			self.drawSleepTask(time, task)

			#
			return self.completeTask(task, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def drawSleepTask(self, time, task):
		if self.context is not None:
			self.context.drawHLine(task.proc, time, task.delay, -self.context.sleep_height, 'std')	
		 
	def executeComputeTask(self, time, task):
		if self.procs[task.proc] <= time:
			# noise
			#noise = self.getHostNoise(task.delay)
			noise = 0
			#TODO

			# forward proc
			self.procs[task.proc] = time + task.delay + noise

			# visual 
			self.drawCompute(task, time, noise)
			
			return self.completeTask(task, self.procs[task.proc])
		else:
			return [(self.procs[task.proc], task)]

	def drawCompute(self, task, time, noise):		
		if self.context is not None:
			self.context.drawRectangle(task.proc, time, task.delay, Visual.compute_base, Visual.compute_height, 'std')

			if self.host_noise is not None:
				self.context.drawRectangle(task.proc, time+task.delay, noise, -self.context.compute_height/2, self.context.compute_height, 'err')

	def executePutTask(self, time, task):
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

		
		return self.completeTask(task, time_put)

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
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = pipelining

	def getMaximumTime(self):
		return self.maximum_time

	def executePutTask(self, time, task):
		# 
		if self.procs[task.proc] > time:
			# fail
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

		# draw put side
		self.drawPut(task, time_pipe, arrival, noise_put)

		#
		if task.block:
			self.procs[task.proc] = time_put
		else:
			self.procs[task.proc] = time_pipe
		self.maximum_time = max(self.maximum_time, time_put)

		return self.completeTask(task, time_put)

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
