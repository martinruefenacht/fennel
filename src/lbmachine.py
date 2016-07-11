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
		self.block_type = 'ack'

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
			if self.host_noise is not None:
				noise = self.host_noise.generate(task.delay)
				self.procs[task.proc] = time + task.delay + noise
			else:
				self.procs[task.proc] = time + task.delay
			
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
		remote = arrival + noise_put

		# draw put side
		self.drawPut(task, time, arrival, noise_put)

		#
		if self.block_type == 'non':
			self.procs[task.proc] = time
			self.maximum_time = max(self.maximum_time, time, remote)
			return True, remote 

		# 
		elif self.block_type == 'arr':
			self.procs[task.proc] = remote
			self.maximum_time = max(self.maximum_time, remote)
			return True, remote 

		#
		else:
			# ack msg
			ack_time = self.alpha
			noise_ack = self.getNetworkNoise(ack_time)
			ack_recv = remote + ack_time

			# draw ack msg
			self.drawAck(task, remote, ack_recv, noise_ack)

			# 
			self.procs[task.proc] = ack_recv + noise_ack


			self.maximum_time = max(self.maximum_time, ack_recv)

			# 
			return True, remote
	
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
			
	def drawAck(self, task, time, arrival, noise):
		# check for visual context
		if self.context:
			side = 1 if task.proc < task.target else -1
	
			# draw ack msg
			self.context.drawSLine(task.target, time, Visual.put_offset, task.proc, arrival, 'sec')
			self.context.drawVLine(task.proc, arrival, Visual.put_base, Visual.put_offset*side, 'sec')

			if noise != 0:
				self.context.drawHLine(task.proc, arrival, noise, Visual.put_offset*side, 'err')	
				self.context.drawVLine(task.proc, arrival+noise, Visual.put_base, Visual.put_offset*side, 'err')

class LBPMachine(LBMachine):
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = pipelining

	def executePutTask(self, time, task):
		if self.procs[task.proc] <= time:
			# issuing message
			if self.host_noise:
				lnoise = self.host_noise.generate(self.kappa)
				local = time + self.kappa + lnoise
			else:
				local = time + self.kappa

			# remote arrival
			if self.network_noise:
				noise_send = self.network_noise.generate(best)
				noise_recv = self.network_noise.generate(self.alpha)

				remote = local + self.alpha + self.beta * task.size
				
			else:
				remote = local + self.alpha + self.beta * task.size

			# ack

			if task.block:
				self.procs[task.proc] = remote + self.alpha
			else:
				self.procs[task.proc] = local

			# max time including control messages
			self.maximum_time = max(self.maximum_time, remote + self.alpha)
			
			success = True
			time_done = remote
		else:
			success = False
			time_done = self.procs[task.proc]

		#if self.context is not None and success:
		#	self.visualizePutTask(time, task, time_done)

		return success, time_done
			
	def visualizePutTask(self, time, task, onoise, inoise):
		yheight = self.context.put_height
		yoffset = self.context.put_offset
		
		side = -1 if task.proc > task.target else 1

		# pipeline
		self.context.drawVLine(task.proc, time, 0.0, (yoffset+yheight)*side)
		self.context.drawVLine(task.proc, time + self.kappa, 0.0, (yoffset+yheight)*side)
		self.context.drawRectangle(task.proc, time, self.kappa, yoffset*side, yheight * side) 

		# main message
		self.context.drawSLine(task.proc, time+self.kappa, yoffset+yheight, task.target, time_done)
		self.context.drawVLine(task.target, time_done, 0.0, (yoffset+yheight)*-side)

		if self.network_noise is not None:
			# draw main message noise
			self.context.drawHLine(task.target, time+best, onoise, -yoffset, 'err')	
			self.context.drawVLine(task.target, time+best+onoise, 0.0, -yoffset, 'err')

		# draw control message
		self.context.drawSLine(task.target, time_done, yoffset+yheight, task.proc, time_done + self.alpha, 'sec')
		self.context.drawVLine(task.proc, time_done+self.alpha, 0.0, (yoffset+yheight)*side, 'err')

		if self.network_noise is not None:
			# draw network noise
			self.context.drawHLine(task.proc, time+best+onoise+self.alpha, inoise, yoffset, 'err')	
			self.context.drawVLine(task.proc, self.procs[task.proc], 0.0, yoffset, 'err')

