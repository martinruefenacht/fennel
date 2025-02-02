import re
import networkx as nx

from tasks import *
from program import *

patterns = [
			r'\s*rank (\d+) {$',
			r'\s*}',
			r'\s*l(\d+):\s*start\s*(?:(\d+)ns)?$',
			r'\s*l(\d+):\s*put\s*(\d+)b to r(\d+)\s*(blocking)?$',
			r'\s*l(\d+):\s*compute\s*(\d+)(ns|b)$',
			r'\s*l(\d+):\s*sleep\s*(\d+)ns$',
			r'\s*l(\d+)\s*>\s*(?:r(\d+):)?l(\d+)$'
			]

def parseGOAL(filename):
	# open file
	goalfile = open(filename, 'r')

	# create program
	dependencies = []
	#program = nx.DiGraph()
	program = Program()
	
	current_rank = -1
	
	for line in goalfile:
		for idx, pattern in enumerate(patterns):
			match = re.match(pattern, line)

			if match:
				if idx == 0:
					# rank beginning
					current_rank = int(match.group(1))

				elif idx == 1:
					# rank end
					current_rank = -1

				elif idx == 2:
					if current_rank == -1:
						print('Invalid format due to missing rank block')
						break

					# start
					name = 'r'+str(current_rank)+'l'+str(match.group(1))

					if match.group(2) == None:
						task = StartTask(name, current_rank)
					else:
						task = StartTask(name, current_rank, skew=int(match.group(2)))

					program.dag.add_node(name, {'task':task})

				elif idx == 3:
					if current_rank == -1:
						print('Invalid format due to missing rank block')
						break

					# put
					name = 'r'+str(current_rank)+'l'+str(match.group(1))

					blocking = match.group(4) is not None
	
					task = PutTask(name, current_rank, int(match.group(3)), int(match.group(2)), blocking)
					program.dag.add_node(name, {'task':task})

				elif idx == 4:
					if current_rank == -1:
						print('Invalid format due to missing rank block')
						break

					# compute 
					name = 'r'+str(current_rank)+'l'+str(match.group(1))

					if match.group(3)[0] == 'b':
						task = ComputeTask(name, current_rank, size=int(match.group(2)))
					else:
						task = ComputeTask(name, current_rank, delay=int(match.group(2)))
					program.dag.add_node(name, {'task':task})
				
				elif idx == 5:
					# sleep
					if current_rank == -1:
						print('Invalid format due to missing rank block')
						break

					name = 'r'+str(current_rank)+'l'+str(match.group(1))
					task = SleepTask(name, current_rank, int(match.group(2)))
					program.dag.add_node(name, {'task':task})
					
				elif idx == 6:
					# dependency
					# cache for later once all nodes are read
					dependencies.append((current_rank, match))	
				else:
					print('Failed to match:', current_rank, match.groups())
		
	# resolve dependencies
	for rank, match in dependencies:
		a = 'r'+str(rank)+'l'+str(match.group(1))

		if match.group(2) is not None:
			b = 'r'+str(match.group(2))+'l'+str(match.group(3))
		else:
			b = 'r'+str(rank)+'l'+str(match.group(3))

		program.dag.add_edge(b, a)
	
	return program
