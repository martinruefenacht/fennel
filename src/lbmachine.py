from machine import Machine
from scipy.stats import betaprime
from random import choice

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

		# visual
		self.context = None

	def setHostNoise(a, b, s):
		self.host_noise = betaprime.rvs(a, b, scale=s, size=1000) 

	def setNetworkNoise(a, b, s):
		self.network_noise = betaprime.rvs(a, b, scale=s, size=1000)

	def setVisualContext(self, context):
		self.context = context

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
		if self.context is not None:
			pass
			# draw single |
			
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
		if self.context is not None:
			pass
			# draw ==== parallel line to process line

		#
		return success, time_done
		 
	def executeComputeTask(self, time, task):
		# logic
		if self.procs[task.proc] <= time:
			# noise
			if self.host_noise is not None:
				noise = choice(self.host_noise)
				self.procs[task.proc] = time + task.delay + noise
			else:
				self.procs[task.proc] = time + task.delay
			
			success = True
			time_done = self.procs[task.proc]
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None:
			pass
			# draw rectange on process line

		#
		return success, time_done

	def executePutTask(self, time, task):
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
			# assume control message has not bandwidth
			self.procs[task.proc] = time + self.alpha * 2

			success = True
			time_done = remote
		else:
			success = False
			time_done = self.procs[task.proc]

		# visual
		if self.context is not None:
			# draw |    network operation
			#		\
			#		 \
			#		  |
			pass

		#
		return success, time_done

class LBPMachine(LBMachine):
	def __init__(self, program, latency, bandwidth, pipelining):
		super().__init__(program, latency, bandwidth)

		self.kappa = issue
	
	def executePutTask(self, time, task):
		if self.procs[task.proc] <= time:
			# TODO revise with blocking and non blocking
			local = time + self.kappa
			remote = local + self.alpha + self.beta * task.size

			self.procs[task.proc] = local
			return True, remote
		else:
			return False, self.procs[task.proc]
