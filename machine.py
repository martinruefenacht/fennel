class Model:
	def __init__(self, size):
		self.size = size

		self.alpha = 1500
		self.beta = 10

		# store cpu times
		self.procs = [0] * self.size

		# topology will need to be in here
		# resource noise will need to be in here
	
	def execute(self, task, program):
		time, nid = task

		print(nid, program.node[nid]['type'], time)

		# execute model specific function
		if program.node[nid]['type'] == 'start':
			com_time = time
		elif program.node[nid]['type'] == 'put':
			if self.procs[program.node[nid]['proc']] <= time:
				com_time = time + self.alpha + self.beta * program.node[nid]['size']
				self.procs[program.node[nid]['proc']] = com_time
			else:
				return [(self.procs[program.node[nid]['proc']], task[1])]
					
		elif program.node[nid]['type'] == 'compute':
			if self.procs[program.node[nid]['proc']] <= time:
				com_time = time + program.node[nid]['delay']
				self.procs[program.node[nid]['proc']] = com_time
			else:
				return [(self.procs[program.node[nid]['proc']], task[1])]
		elif program.node[nid]['type'] == 'end':
			com_time = time

		else:
			print('not implemented', program.node[nid]['type'])

		# increment depend counter for all successors
		tasks = []
		for snid in program.successors_iter(nid):
			program.node[snid]['depend'] += 1
			program.node[snid]['time'] = max(com_time, program.node[snid]['time']) 

			# check if all dependencies were met
			if program.node[snid]['depend'] == program.in_degree([snid])[snid]:
				t = (max(com_time, program.node[snid]['time']), snid)
				tasks.append(t)

		return tasks
