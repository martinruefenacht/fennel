from scipy.stats import betaprime
from heapq import *
from tasks import *

class Machine:
	def __init__(self, program):
		self.program = program

		self.dependencies = {}
		self.dtimes = {}

	def run(self):
		taskqueue = []
		
		# insert all start tasks
		for task in self.program.getStartTasks():
			heappush(taskqueue, (0, task))

		# process entire queue
		while taskqueue:
			# retrieve next global clock event
			time, task = heappop(taskqueue)

			# execute task
			successors = self.execute(time, task)

			# insert all successor tasks
			for successor in successors:
				heappush(taskqueue, successor)

	def completeTask(self, task, time):
		successors = []

		for successor in self.program.getSuccessorTasks(task.node):
			# increment completed dependencies for successor
			self.dependencies[successor] = self.dependencies.get(successor, 0) + 1

			# forward task to last dependency
			self.dtimes[successor] = max(self.dtimes.get(successor, 0), time)

			# check for completion
			if self.dependencies[successor] == self.program.dag.in_degree(successor):
				successor_task = self.program.getTask(successor)
				
				successors.append((self.dtimes[successor], successor_task))

		return successors


	def execute(self, time, task):
		# StartTask
		if isinstance(task, StartTask):
			success, time_done = self.executeStartTask(time, task)
		
		# ProxyTask
		elif isinstance(task, ProxyTask):
			success, time_done = self.executeProxyTask(time, task)
		
		# ComputeTask
		elif isinstance(task, ComputeTask):
			success, time_done = self.executeComputeTask(time, task)
		
		# PutTask
		elif isinstance(task, PutTask):
			success, time_done = self.executePutTask(time, task)

		# GetTask
		elif isinstance(task, GetTask):
			success, time_done = self.executePutTask(time, task)

		# Unknown
		else:
			print('Unknown task type:', task, '@', time, 'on', task.proc)

		# check task execution
		if not success:
			# reinsert task
			return [(time_done, task)]
		else:
			# insert successor tasks
			return self.completeTask(task, time_done)

	def executeStartTask(self, time, task):
		raise NotImplementedError

	def executeProxyTask(self, time, task):
		raise NotImplementedError

	def executeSleepTask(self, time, task):
		raise NotImplementedError

	def executeComputeTask(self, time, task):
		raise NotImplementedError

	def executePutTask(self, time, task):
		raise NotImplementedError

	def executeGetTask(self, time, task):
		raise NotImplementedError
