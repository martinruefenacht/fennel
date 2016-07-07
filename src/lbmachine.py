from machine import Machine
from scipy.stats import betaprime
from random import choice
import math

class LBMachine(Machine):
	def __init__(self, program, latency, bandwidth):
		super().__init__(program)

		# model parameters
		self.alpha = latency
		self.beta = bandwidth

		# process times
		self.procs = [0] * program.getSize()

		# noise
		self.host_noise = None
		self.network_noise = None

	def setHostNoise(a, b, s):
		self.host_noise = betaprime.rvs(a, b, scale=s, size=1000) 

	def setNetworkNoise(a, b, s):
		self.network_noise = betaprime.rvs(a, b, scale=s, size=1000)

	def drawMachine(self):
		# find max time
		max_time = int(math.ceil(max(self.procs) / 1000)) * 1000

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
			self.context.drawVLine(task.proc, time, 0.2, 0.2)
			self.context.drawCircle(task.proc, time, -0.2, 0.075)
			
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
			self.context.drawHLine(task.proc, time, task.delay, -0.1)	

		#
		return success, time_done
		 
	def executeComputeTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# noise
			#if self.host_noise is not None:
			#	noise = choice(self.host_noise)
			#	self.procs[task.proc] = time + task.delay + noise
			#else:
			self.procs[task.proc] = time + task.delay
			
			success = True
			time_done = self.procs[task.proc]
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None and success:
			self.context.drawRectangle(task.proc, time, task.delay)

		#
		return success, time_done

	def executePutTask(self, time, task):
		# puts under Latency-Bandwidth are always blocking
		
		# logic
		if self.procs[task.proc] <= time:
			# noise
			if self.host_noise is not None:
				# TODO implement network noise
				pass
			if self.network_noise is not None:
				# TODO implement network noise
				pass

			# remote arrival time = RTT/2
			remote = time + self.alpha + self.beta * task.size

			# local completion time = RTT
			# assume control message has not bandwidth, small message
			self.procs[task.proc] = remote + self.alpha

			success = True
			time_done = remote
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None and success:
			# main message
			self.context.drawVLine(task.proc, time, 0.0, 0.15)
			self.context.drawSLine(task.proc, time, 0.15, task.target, time_done)
			self.context.drawVLine(task.target, time_done, 0.0, -0.15)

			# draw control message
			self.context.drawSLine(task.target, time_done, -0.15, task.proc, self.procs[task.proc])
			self.context.drawVLine(task.proc, self.procs[task.proc], 0.0, 0.15)
			
		#
		return success, time_done

class LBPMachine(LBMachine):
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = pipelining
	
	def executePutTask(self, time, task):
		if self.procs[task.proc] <= time:
			# issue
			local = time + self.kappa

			# remote arrival
			remote = local + self.alpha + self.beta * task.size

			# ack

			if task.block:
				self.procs[task.proc] = remote + self.alpha
			else:
				self.procs[task.proc] = local
			return True, remote
		else:
			return False, self.procs[task.proc]
