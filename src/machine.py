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
			heappush(taskqueue, task)

		# process entire queue
		while taskqueue:
			# retrieve next global clock event
			task = heappop(taskqueue)

			# execute task
			successors = self.execute(task)

			# insert all successor tasks
			for successor in successors:
				heappush(taskqueue, successor)

	def completeTask(self, task, time):
		successors = []

		for successor in self.program.getSuccessorTasks(task.node):
			# increment completed dependencies for successor
			if successor in self.dependencies:
				self.dependencies[successor] += 1
			else:
				self.dependencies[successor] = 1

			# forward task to last dependency
			self.dtimes[successor] = max(self.dtimes.get(successor, 0), time)

			# check for completion
			if self.dependencies[successor] == self.program.dag.in_degree(successor):
				successor_task = self.program.getTask(successor)
				successor_task.time = self.dtimes[successor]
				
				successors.append(successor_task)

		return successors


	def execute(self, task):
		# StartTask
		if isinstance(task, StartTask):
			success, time = self.executeStartTask(task)
		
		# ProxyTask
		elif isinstance(task, ProxyTask):
			success, time = self.executeProxyTask(task)
		
		# ComputeTask
		elif isinstance(task, ComputeTask):
			success, time = self.executeComputeTask(task)
		
		# PutTask
		elif isinstance(task, PutTask):
			success, time = self.executePutTask(task)

		# Unknown
		else:
			print('Unknown task type:', task)

		# check task execution
		if not success:
			# reinsert task
			return [task]
		else:
			# insert successor tasks
			return self.completeTask(task, time)

	def executeStartTask(self, task):
		raise NotImplementedError

	def executeProxyTask(self, task):
		raise NotImplementedError

	def executeSleepTask(self, task):
		raise NotImplementedError

	def executeComputeTask(self, task):
		raise NotImplementedError

	def executePutTask(self, task):
		raise NotImplementedError
