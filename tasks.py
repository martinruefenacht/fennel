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
	def __init__(self, node, proc):
		super().__init__(node, proc)

	def execute(self, machine, time):
		machine.record[self.node] = time
		
		return (True, time)

class ComputeTask(Task):
	gamma = 10

	def __init__(self, node, proc, delay=None, size=None):
		# initialize task
		super().__init__(node, proc)

		# initialize compute task
		if size is None and delay is not None:
			self.delay = delay
		elif size is not None and delay is None:
			self.delay = ComputeTask.gamma * size
		else:
			print('ComputeTask was not constructed properly.')

	def execute(self, machine, time):
		rank_time = machine.getRankTime(self.proc)
		
		if time >= rank_time:
			# TODO add noise machine

			# forward rank in time
			machine.setRankTime(self.proc, time + self.delay)

			# record task time for machine
			machine.record[self.node] = time

			# can forward
			return (True, time + self.delay)
		else:
			# delay
			return (False, rank_time) 
			
class PutTask(Task):
	alpha_p = 1600
	alpha_r = 400
	beta = 10

	def __init__(self, node, proc, target, size):
		super().__init__(node, proc)
		self.target = target
		self.size = size

	def execute(self, machine, time):
		rank_time = machine.getRankTime(self.proc)

		if time >= rank_time:
			# local time occupied
			local = PutTask.alpha_r
			remote = PutTask.alpha_p + PutTask.beta * self.size

			# record	
			machine.record[self.node] = [time, local, remote]
	
			# modify state
			machine.setRankTime(self.proc, time + local)

			return (True, time + local + remote)
		else:
			return (False, rank_time)
