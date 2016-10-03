from heapq import *
import libpqueue

import simulator.core.tasks as tasks

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

		# visual context
		self.context = None

	def reset(self):
		self.dependencies = {}
		self.dtimes = {}

	def getMaximumTime(self):
		raise NotImplementedError

	def setVisual(self, context):
		self.context = context

	def drawMachine(self):
		# find max time
		max_time = int((math.ceil(self.getMaximumTime() / 500) * 500))

		# draw time line
		self.context.drawTimeLine(max_time)

		# draw process lines
		self.context.drawProcessLines(self.program.getSize(), max_time)

	def run(self):
		#taskqueue = []
		taskqueue = libpqueue.PriorityQueue(self.program.getProcessCount()*1000)
		
		# insert all start tasks
		for task in self.program.getStartTasks():
			#heappush(taskqueue, (0, task))
			taskqueue.push(0, task)

		# process entire queue
		#while taskqueue:
		while not taskqueue.isEmpty():
			# retrieve next global clock event
			#time, task = heappop(taskqueue)
			time, task = taskqueue.pop()
			
			# execute task
			successors = self.execute(time, task)

			# insert all successor tasks
			for successor in successors:
				#heappush(taskqueue, successor)
				taskqueue.push(*successor)

		# visualize
		if self.context is not None:
			self.drawMachine()

	def completeTask(self, task, time):
		successors = []

		for successor in self.program.getSuccessors(task.node):
			# increment completed dependencies for successor
			self.dependencies[successor] = self.dependencies.get(successor, 0) + 1

			# forward task to last dependency
			self.dtimes[successor] = max(self.dtimes.get(successor, 0), time)

			# check for completion
			if self.dependencies[successor] == self.program.getInDegree(successor):
				successor_task = self.program.getTask(successor)
				time_next = self.dtimes[successor]

				# delete record of program
				del self.dtimes[successor]
				del self.dependencies[successor]
				
				successors.append((time_next, successor_task))

		return successors


	def execute(self, time, task):
		# look up task handler and execute 
		return self.task_handlers[task.__class__.__name__](time, task)
