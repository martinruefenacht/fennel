from abc import ABCMeta, abstractmethod

class Task(metaclass=ABCMeta):
	task_counter = 0	

	def __init__(self, node, proc):
		self.node = node
		self.proc = proc

		self.taskid = Task.task_counter
		Task.task_counter += 1

	def __lt__(self, task):
		return self.taskid < task.taskid

	@abstractmethod
	def execute(self, machine, time):
		pass

class StartTask(Task):
	def __init__(self, node, proc, skew=None):
		super().__init__(node, proc)

		self.skew = skew

	def execute(self, machine, time):
		# TODO if time is not 0 something has gone terribly wrong		

		# TODO incoming skew!!!
		# should probably be definable

		machine.record[self.node] = time
		
		#return (True, time + self.skew)
		return (True, time)

class SleepTask(Task):
	def __init__(self, node, proc, delay):
		super().__init__(node, proc)

		self.delay = delay

	def execute(self, machine, time):
		rank_time = machine.getRankTime(self.proc)
	
		if time >= rank_time:
			# get noise
			noise = machine.getHostNoise(time, self.delay)
			
			machine.record[self.node] = [time, self.delay, noise]

			machine.setRankTime(self.proc, time + self.delay + noise)

			return (True, time + self.delay + noise)
		else:
			return (False, rank_time)

class ComputeTask(Task):
	def __init__(self, node, proc, delay=None, size=None):
		# initialize task
		super().__init__(node, proc)

		# initialize copute task
		if size is None and delay is not None:
			self.delay = delay
			self.size = None 
		elif size is not None and delay is None:
			self.size = size
			self.delay = None
		else:
			print('ComputeTask was not constructed properly.')

	def execute(self, machine, time):
		rank_time = machine.getRankTime(self.proc)
		
		if time >= rank_time:
			# calculate delay for compute based on machine
			delay = self.delay
			if delay is None:
				delay = self.size * machine.gamma

			# get noise
			noise = machine.getHostNoise(time, delay)

			# forward rank in time
			machine.setRankTime(self.proc, time + delay + noise)

			# record task time for machine
			machine.record[self.node] = [time, delay, noise]

			# next task time
			return (True, time + delay + noise)
		else:
			# delay
			return (False, rank_time) 
			
class PutTask(Task):
	def __init__(self, node, proc, target, size):
		super().__init__(node, proc)
		self.target = target
		self.size = size

	def execute(self, machine, time):
		rank_time = machine.getRankTime(self.proc)

		if time >= rank_time:
			# local time occupied
			local = machine.alpha_r
			remote = machine.alpha_p + machine.beta * self.size
			lnoise = machine.getHostNoise(time, local)
			rnoise = machine.getNetworkNoise(time, remote)

			# record	
			machine.record[self.node] = [time, local, remote, lnoise, rnoise]
	
			# modify state
			machine.setRankTime(self.proc, time + local + lnoise)

			return (True, time + local + lnoise + remote + rnoise)
		else:
			return (False, rank_time)
