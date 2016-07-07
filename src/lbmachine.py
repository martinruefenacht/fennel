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

			self.context.drawVLine(task.proc, time, start_height, start_height)
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
			self.context.drawHLine(task.proc, time, task.delay, -self.context.sleep_height)	

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
			self.context.drawRectangle(task.proc, time, task.delay, -self.context.compute_height/2, self.context.compute_height)

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
			#self.procs[task.proc] = remote + self.alpha
			self.procs[task.proc] = remote + self.alpha

			success = True
			time_done = remote
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None and success:
			self.visualizePutTask(time, task, time_done)
			
		#
		return success, time_done

	def visualizePutTask(self, time, task, time_done):
		yoffset = 0.15

		if task.proc > task.target:
			yoffset *= -1

		# main message
		self.context.drawVLine(task.proc, time, 0.0, yoffset)
		self.context.drawSLine(task.proc, time, 0.15, task.target, time_done)

		self.context.drawVLine(task.target, time_done, 0.0, -yoffset)

		# draw control message
		self.context.drawSLine(task.target, time_done, 0.15, task.proc, self.procs[task.proc], primary=False)
		self.context.drawVLine(task.proc, self.procs[task.proc], 0.0, yoffset, primary=False)

class LBPMachine(LBMachine):
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = pipelining

		self.maxtime = 0

	def getMaxTime(self):
		return self.maxtime
	
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

			# max time including control messages
			self.maxtime = max(self.maxtime, remote + self.alpha)
			
			success = True
			time_done = remote
		else:
			success = False
			time_done = self.procs[task.proc]

		if self.context is not None and success:
			self.visualizePutTask(time, task, time_done)

		return success, time_done
			
	def visualizePutTask(self, time, task, time_done):
		yheight = self.context.put_height
		yoffset = self.context.put_offset
		
		side = -1 if task.proc > task.target else 1

		# pipelin
		self.context.drawVLine(task.proc, time, 0.0, (yoffset+yheight)*side)
		self.context.drawVLine(task.proc, time + self.kappa, 0.0, (yoffset+yheight)*side)
		self.context.drawRectangle(task.proc, time, self.kappa, yoffset*side, yheight * side) 

		# main message
		self.context.drawSLine(task.proc, time+self.kappa, yoffset+yheight, task.target, time_done)
		self.context.drawVLine(task.target, time_done, 0.0, (yoffset+yheight)*-side)

		# draw control message
		self.context.drawSLine(task.target, time_done, yoffset+yheight, task.proc, time_done + self.alpha, primary=False)
		self.context.drawVLine(task.proc, time_done+self.alpha, 0.0, (yoffset+yheight)*side, primary=False)
