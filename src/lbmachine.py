from machine import Machine
from scipy.stats import betaprime
from random import choice
import math

from visual import Visual

class LBMachine(Machine):
	def __init__(self, program, latency, bandwidth):
		super().__init__(program)

		# model parameters
		self.alpha = latency
		self.beta = bandwidth

		# recording
		self.recording = False

		# process times
		self.procs = [0] * program.getSize()

		# noise
		self.noise_record = {}
		self.host_noise = None
		self.network_noise = None

	def getMaxTime(self):
		return max(self.procs)	

	def drawMachine(self):
		# find max time
		max_time = int((math.ceil(self.getMaxTime() / 1000) * 1000))

		# draw time line
		self.context.drawTimeLine(max_time)

		# draw process lines
		self.context.drawProcessLines(self.program.getSize(), max_time)

	def executeStartTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# no noise

			self.procs[task.proc] = time + task.skew
			
			success = True
			time_done = time + task.skew
		else:
			success = False
			time_done = time

		# visual
		if self.context is not None and success:
			start_height = self.context.start_height
			start_radius = self.context.start_radius

			self.context.drawVLine(task.proc, time, start_height, start_height, 'std')
			self.context.drawCircle(task.proc, time, -start_height, start_radius)
			
		# 
		return success, time_done

	def executeProxyTask(self, time, task):
		# logic
		self.procs[task.proc] = time

		# no noise

		# no visual

		#
		return True, time

	def executeSleepTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			self.procs[task.proc] = time + task.delay

			success = True
			time_done = self.procs[task.proc]
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None and success:
			self.context.drawHLine(task.proc, time, task.delay, -self.context.sleep_height, 'std')	

		#
		return success, time_done
		 
	def executeComputeTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# noise
			noise = self.getHostNoise(task.delay)
			self.procs[task.proc] = time + task.delay + noise
			
			success = True
			time_done = self.procs[task.proc]
		else:
			success = False
			time_done = self.procs[task.proc]

		# record
		if self.recording:
			self.noise_record[task.name] = [noise]

		# visual
		if self.context is not None and success:
			self.context.drawRectangle(task.proc, time, task.delay, -self.context.compute_height/2, self.context.compute_height, 'std')
			if self.host_noise is not None:
				self.context.drawRectangle(task.proc, time+task.delay, noise, -self.context.compute_height/2, self.context.compute_height, 'err')

		#
		return success, time_done

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

	def executePutTask(self, time, task):
		# 
		if self.procs[task.proc] > time:
			# fail
			return False, self.procs[task.proc]

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
		return True, time_put 

	def drawPut(self, task, time, arrival, noise):
		# check for visual context
		if self.context:
			side = 1 if task.proc < task.target else -1
			
			# draw put msg
			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_offset*side, 'std')
			self.context.drawSLine(task.proc, time, Visual.put_offset, task.target, arrival, 'std')
			self.context.drawVLine(task.target, arrival, Visual.put_base, Visual.put_offset*-side, 'std')
		
			# draw noise
			if noise != 0:
				self.context.drawHLine(task.target, arrival, noise, -Visual.put_offset*side, 'err')	
				self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_offset*side, 'err')
			
class LBPMachine(LBMachine):
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = pipelining

	def executePutTask(self, time, task):
		# 
		if self.procs[task.proc] > time:
			# fail
			return False, self.procs[task.proc]

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
		self.maximum_time = max(self.maximum_time, time_pipe)
		return True, time_put 

	def drawPipe(self, task, time, delay, noise):
		#
		if self.context:
			side = 1 if task.proc < task.target else -1

			self.context.drawVLine(task.proc, time, Visual.put_base, Visual.put_offset*side, 'std')
			self.context.drawHLine(task.proc, time, delay, Visual.put_offset*side, 'std')
			
			if noise != 0:
				self.context.drawHLine(task.proc, time+delay, noise, Visual.put_offset*side, 'err')
	
	def drawPut(self, task, time, arrival, noise):
		# check for visual context
		if self.context:
			side = 1 if task.proc < task.target else -1
			
			# draw put msg
			self.context.drawSLine(task.proc, time, Visual.put_offset, task.target, arrival, 'std')
			self.context.drawVLine(task.target, arrival, Visual.put_base, Visual.put_offset*-side, 'std')
		
			# draw noise
			if noise != 0:
				self.context.drawHLine(task.target, arrival, noise, -Visual.put_offset*side, 'err')	
				self.context.drawVLine(task.target, arrival+noise, Visual.put_base, -Visual.put_offset*side, 'err')
