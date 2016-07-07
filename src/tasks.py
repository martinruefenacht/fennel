class Task:
	task_counter = 0	

	def __init__(self, node, proc):
		self.node = node
		self.proc = proc

		self.taskid = Task.task_counter
		Task.task_counter += 1

	def __lt__(self, task):
		return self.taskid < task.taskid

class StartTask(Task):
	def __init__(self, node, proc, skew=0):
		super().__init__(node, proc)

		# 
		self.skew = skew
		
class ProxyTask(Task):
	def __init__(self, node, proc):
		super().__init__(node, proc)

class SleepTask(Task):
	def __init__(self, node, proc, delay):
		# initialize Task
		super().__init__(node, proc)

		# initialize SleepTask
		self.delay = delay

class ComputeTask(Task):
	def __init__(self, node, proc, delay):
		# initialize task
		super().__init__(node, proc)
		
		# TODO support data size?

		# initialize compute task
		self.delay = delay

class PutTask(Task):
	def __init__(self, node, proc, target, size, block=False):
		super().__init__(node, proc)
		self.target = target
		self.size = size
		self.block = block

class GetTask(Task):
	def __init__(self, node, proc, target, size, block=False):
		self.target = target
		self.size = size
		self.block = block

class SendTask(Task):
	def __init__(self, node, proc, target, size, block=False):
		pass

class RecvTask(Task):
	def __init__(self, node, proc, target, size, block=False):
		pass
