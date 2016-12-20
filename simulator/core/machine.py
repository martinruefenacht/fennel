import heapq
import math
#import libpqueue

import simulator.core.tasks as tasks

class Machine:
	def __init__(self, nodes):
		self.node_count = nodes

		# fulfilled dependency counter
		self.dependencies = {}

		# max time of dependency, gives task begin time
		# starts will not be included
		self.dtimes = {}

		# task handlers
		self.task_handlers = {}

		# program counter
		self.program_counter = 0

		# visual context
		self.context = None

	def reset(self):
		self.dependencies = {}
		self.dtimes = {}

	def getMaximumTime(self):
		raise NotImplementedError

	def setVisual(self, context):
		self.context = context

	def registerVisualContext(self, context):
		self.context = context	

	def drawMachine(self):
		# find max time
		max_time = int((math.ceil(self.getMaximumTime() / 500) * 500))

		# draw time line
		self.context.drawTimeLine(max_time)

		# draw process lines
		self.context.drawProcessLines(self.node_count, max_time)

	def run(self, program):
		if program.getProcessCount() > self.node_count:
			raise ValueError

		# TODO remove magic 1000, require some intelligent way of memory requirement
		# (technically program should know)
		#taskqueue = libpqueue.PriorityQueue(program.getProcessCount() * 1000)
		taskqueue = []
		
		# insert all start tasks
		for task in program.getStartTasks():
			#taskqueue.push(0, task)
			heapq.heappush(taskqueue, (0, task))

		# process entire queue
		#while not taskqueue.isEmpty():
		while taskqueue:
			# retrieve next global clock event
			#time, task = taskqueue.pop()
			time, task = heapq.heappop(taskqueue)

			# execute task
			successors = self.execute(time, program, task)

			# insert all successor tasks
			for successor in successors:
				#taskqueue.push(*successor)
				heapq.heappush(taskqueue, successor)

		# visualize
		if self.context is not None:
			self.drawMachine()

	def completeTask(self, task, program, time):
		successors = []

		for successor in program.getSuccessors(task.node):
			# increment completed dependencies for successor
			self.dependencies[successor] = self.dependencies.get(successor, 0) + 1

			# forward task to last dependency
			self.dtimes[successor] = max(self.dtimes.get(successor, 0), time)

			# check for completion
			if self.dependencies[successor] == program.getInDegree(successor):
				successor_task = program.getTask(successor)
				time_next = self.dtimes[successor]

				# delete record of program
				del self.dtimes[successor]
				del self.dependencies[successor]
				
				successors.append((time_next, successor_task))

		return successors


	def execute(self, time, program, task):
		# look up task handler and execute 
		return self.task_handlers[task.__class__.__name__](time, program, task)
