import simulator.core.stage as stage

class Schedule:
	def __init__(self, process_count, order):
		self.process_count = process_count
		self.order = order

	def addStage(self, stage):
		self.order.append(stage)

	def getProcessCount(self):
		return self.process_count

	def __iter__(self):
		for stage in self.order:
			yield stage 

	def __str__(self):
		return str(self.process_count) + ':' + str(self.order)

	def __repr__(self):
		pass
