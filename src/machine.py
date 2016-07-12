from scipy.stats import betaprime
from heapq import *
from tasks import *

class Machine:
	def __init__(self, program):
		self.program = program

		# fulfilled dependency counter
		self.dependencies = {}

		# max time of dependency, gives task begin time
		# starts will not be included
		self.dtimes = {}

		# task handlers
		self.task_handlers = {}

		# maximum time
		self.maximum_time = 0

		# visual context
		self.context = None

	def getMaximumTime(self):
		return self.maximum_time

	def setVisual(self, context):
		self.context = context

	def drawMachine(self):
		raise NotImplementedError

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

		# visualize
		if self.context is not None:
			self.drawMachine()

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
				time_next = self.dtimes[successor]

				# delete record of program
				del self.dtimes[successor]
				del self.dependencies[successor]
				
				successors.append((time_next, successor_task))

		return successors


	def execute(self, time, task):
		handled = False

		# search all task handlers for task
		for tasktype, handler in self.task_handlers.items():
			if isinstance(task, tasktype):
				# TODO need to more array return of tasks into handler
				return handler(time, task)
		
		print('Unknown task type:', task)
		raise NotImplementedError
