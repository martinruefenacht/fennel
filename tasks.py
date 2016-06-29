from abc import ABCMeta, abstractmethod
from random import choice
from scipy.stats import betaprime

class Task(metaclass=ABCMeta):
	task_counter = 0	

	def __init__(self, name, proc):
		self.proc = proc
		self.name = name

		self.time = -1 
		self.taskid = Task.task_counter
		self.dependencies = 0
		Task.task_counter += 1

	def __lt__(self, task):
		if self.time == task.time:
			return self.taskid < task.taskid
		else:
			return self.time < task.time

	@abstractmethod
	def execute(self, machine, context=None):
		pass

class StartTask(Task):
	def __init__(self, name, proc, time=0):
		super().__init__(name, proc)
		self.time = time

	def execute(self, machine, context=None):
		return self.time

class ComputeTask(Task):
	gamma = 10

	def __init__(self, name, proc, delay=None, size=None):
		# initialize task
		super().__init__(name, proc)

		# initialize compute task
		if size is None and delay is not None:
			self.delay = delay
		elif size is not None and delay is None:
			self.delay = gamma * size
		else:
			print('ComputeTask was not constructed properly.')

		# setup noise profile
		self.noise = [int(round(i)) for i in betaprime.rvs(2, 3, loc=0, scale=20, size=1000)]

	def execute(self, machine, context=None):
		# check if proc is available
		if self.time >= machine.procs[self.proc]:
			# calculate forward time
			delay = self.delay
		
			# add noise
			if self.noise is not None:
				noise = choice(self.noise)
			else:
				noise = 0
	
			# forward proc
			machine.procs[self.proc] = self.time + delay + noise

			# visualize
			if context:
				# draw delay
				context.rectangle(10+self.time/10, 18-2+36*self.proc, delay/10, 4)
				context.fill()
				
				# draw noise
				context.set_source_rgb(1.0, 0.0, 0.0)
				if noise != 0:
					context.rectangle(10+self.time/10+delay/10, 18-2+36*self.proc, noise/10, 4)
					context.fill()
				context.set_source_rgb(0.0, 0.0, 0.0)
			
			# next event time 
			return self.time + delay + noise
		# proc not available
		else:
			# delay event until proc available
			self.time = machine.procs[self.proc]

			# reinsert self task into task queue
			return None

class PutTask(Task):
	alpha_p = 1600
	alpha_r = 400
	beta = 10

	def __init__(self, name, proc, target, size):
		super().__init__(name, proc)
		self.target = target
		self.size = size

		self.local_noise = [int(round(i)) for i in betaprime.rvs(2, 3, loc=10, scale=20, size=1000)]
		self.remote_noise = [int(round(i)) for i in betaprime.rvs(2, 3, loc=10, scale=20, size=1000)]
	
	def execute(self, machine, context=None):
		if self.time >= machine.procs[self.proc]:
			# local time occupied
			local = PutTask.alpha_r

			if self.local_noise is not None:
				lnoise = choice(self.local_noise)
			else:
				lnoise = 0

			# remote arrival time
			remote = local + PutTask.alpha_p
			
			if self.remote_noise is not None:
				rnoise = choice(self.remote_noise)
			else:
				rnoise = 0

			# visualize
			if context:
				context.rectangle(10+self.time/10, 18-1+36*self.proc, local/10, 2)
				context.fill()

				if self.target - self.proc > 0:
					diff = 3
				else:
					diff = -3

				context.move_to(10+(self.time+local)/10, 18+36*self.proc)
				context.line_to(10+(self.time+local)/10,18+36*self.proc+diff)
				context.line_to(10+(self.time+remote)/10, 18+36*(self.target)-diff)
				context.line_to(10+(self.time+remote)/10, 18+36*self.target)
				context.stroke()
		
				context.set_source_rgb(1,0,0)
				if lnoise != 0:
					context.rectangle(10+self.time/10+local/10,18-1+36*self.proc, lnoise/10, 2)
					context.fill()

				if rnoise != 0:
					context.move_to(10+(self.time+local+lnoise)/10, 18+36*self.proc)
					context.line_to(10+(self.time+local+lnoise)/10,18+36*self.proc+diff)
					context.line_to(10+(self.time+remote+lnoise)/10, 18+36*self.target-diff)
					context.line_to(10+(self.time+remote+lnoise+rnoise)/10, 18+36*(self.target)-diff)
					context.line_to(10+(self.time+remote+lnoise+rnoise)/10, 18+36*self.target)
					context.stroke()
				
				context.set_source_rgb(0,0,0)

			# modify state
			machine.procs[self.proc] = self.time + local + lnoise
			return self.time + remote + lnoise + rnoise
		else:
			self.time = machine.procs[self.proc]
			return None
