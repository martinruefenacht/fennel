#! /usr/bin/python3

from heapq import *
from networkx import *
import cairo, sys

from tasks import *
import visual, parser, machine

class Simulator:
	def __init__(self):
		self.taskqueue = []

	def run(self, machine, program):
		# find all nodes in program without dependencies
		for nid, deg in program.in_degree_iter():
			if deg == 0:
				# insert into task queue
				heappush(self.taskqueue, program.node[nid]['task'])

		# process entire queue
		while self.taskqueue:
			# retrieve next global clock event
			task = heappop(self.taskqueue)

			# execute task
			time = task.execute(machine)

			# check for reschedule
			if time is None:
				# reinsert into task queue
				heappush(self.taskqueue, task)
			else:
				# push sucessors
				for sid in program.successors_iter(task.name):
					suc = program.node[sid]['task']

					# increment dependencies
					suc.dependencies += 1

					# latest dependency
					suc.time = max(time, suc.time)

					# check for complete dependencies
					if suc.dependencies == program.in_degree(sid):
						heappush(self.taskqueue, suc)

if __name__ == "__main__":
	# parse program
	program = parser.parseGOAL(sys.argv[1])

	# a2, a2
	#program.add_node('p0is', {'task':StartTask('p0is', 0)})	
	#program.add_node('p0i1', {'task':PutTask('p0i1', 0, 1, 8)})
	#program.add_node('p0i2', {'task':ComputeTask('p0i2', 0, 100)})
	#program.add_node('p0i3', {'task':PutTask('p0i3', 0, 2, 8)})
	#program.add_node('p0i4', {'task':ComputeTask('p0i4', 0, 100)})
	#
	#program.add_node('p1is', {'task':StartTask('p1is', 1)})	
	#program.add_node('p1i1', {'task':PutTask('p1i1', 1, 0, 8)})
	#program.add_node('p1i2', {'task':ComputeTask('p1i2', 1, 100)})
	#program.add_node('p1i3', {'task':PutTask('p1i3', 1, 3, 8)})
	#program.add_node('p1i4', {'task':ComputeTask('p1i4', 1, 100)})

	#program.add_node('p2is', {'task':StartTask('p2is', 2)})	
	#program.add_node('p2i1', {'task':PutTask('p2i1', 2, 3, 8)})
	#program.add_node('p2i2', {'task':ComputeTask('p2i2', 2, 100)})
	#program.add_node('p2i3', {'task':PutTask('p2i3', 2, 0, 8)})
	#program.add_node('p2i4', {'task':ComputeTask('p2i4', 2, 100)})

	#program.add_node('p3is', {'task':StartTask('p3is', 3)})	
	#program.add_node('p3i1', {'task':PutTask('p3i1', 3, 2, 8)})
	#program.add_node('p3i2', {'task':ComputeTask('p3i2', 3, 100)})
	#program.add_node('p3i3', {'task':PutTask('p3i3', 3, 1, 8)})
	#program.add_node('p3i4', {'task':ComputeTask('p3i4', 3, 100)})

	#program.add_edge('p0is','p0i1')
	#program.add_edge('p0is','p0i2')
	#program.add_edge('p1i1','p0i2')
	#program.add_edge('p0i2','p0i3')
	#program.add_edge('p0i2','p0i4')
	#program.add_edge('p2i3','p0i4')
	#	
	#program.add_edge('p1is','p1i1')
	#program.add_edge('p1is','p1i2')
	#program.add_edge('p0i1','p1i2')
	#program.add_edge('p1i2','p1i3')
	#program.add_edge('p1i2','p1i4')
	#program.add_edge('p3i3','p1i4')

	#program.add_edge('p2is','p2i1')
	#program.add_edge('p2is','p2i2')
	#program.add_edge('p3i1','p2i2')
	#program.add_edge('p2i2','p2i3')
	#program.add_edge('p2i2','p2i4')
	#program.add_edge('p0i3','p2i4')

	#program.add_edge('p3is','p3i1')
	#program.add_edge('p3is','p3i2')
	#program.add_edge('p2i1','p3i2')
	#program.add_edge('p3i2','p3i3')
	#program.add_edge('p3i2','p3i4')
	#program.add_edge('p1i3','p3i4')
	
	
	#program.add_node('p0is', {'task':StartTask('p0is', 0)})	
	#program.add_node('p1is', {'task':StartTask('p1is', 1)})	
	#program.add_node('p2is', {'task':StartTask('p2is', 2)})	
	#program.add_node('p3is', {'task':StartTask('p3is', 3)})	

	#program.add_node('p0i1', {'task':PutTask('p0i1', 0, 1, 8)})
	#program.add_node('p1i1', {'task':PutTask('p1i1', 1, 2, 8)})
	#program.add_node('p2i1', {'task':PutTask('p2i1', 2, 3, 8)})
	#program.add_node('p3i1', {'task':PutTask('p3i1', 3, 0, 8)})

	#program.add_node('p0i2', {'task':PutTask('p0i2', 0, 2, 8)})
	#program.add_node('p1i2', {'task':PutTask('p1i2', 1, 3, 8)})
	#program.add_node('p2i2', {'task':PutTask('p2i2', 2, 0, 8)})
	#program.add_node('p3i2', {'task':PutTask('p3i2', 3, 1, 8)})
	#
	#program.add_node('p0i3', {'task':PutTask('p0i3', 0, 3, 8)})
	#program.add_node('p1i3', {'task':PutTask('p1i3', 1, 0, 8)})
	#program.add_node('p2i3', {'task':PutTask('p2i3', 2, 1, 8)})
	#program.add_node('p3i3', {'task':PutTask('p3i3', 3, 2, 8)})

	#program.add_node('p0i4', {'task':ComputeTask('p0i4', 0, 100)})
	#program.add_node('p1i4', {'task':ComputeTask('p1i4', 1, 100)})
	#program.add_node('p2i4', {'task':ComputeTask('p2i4', 2, 100)})
	#program.add_node('p3i4', {'task':ComputeTask('p3i4', 3, 100)})

	#program.add_edge('p0is','p0i1')
	#program.add_edge('p0is','p0i2')
	#program.add_edge('p0is','p0i3')
	#program.add_edge('p0is','p0i4')
	#program.add_edge('p3i1','p0i4')
	#program.add_edge('p2i2','p0i4')
	#program.add_edge('p1i3','p0i4')

	#program.add_edge('p1is','p1i1')
	#program.add_edge('p1is','p1i2')
	#program.add_edge('p1is','p1i3')
	#program.add_edge('p1is','p1i4')
	#program.add_edge('p0i1','p1i4')
	#program.add_edge('p3i2','p1i4')
	#program.add_edge('p2i3','p1i4')

	#program.add_edge('p2is','p2i1')
	#program.add_edge('p2is','p2i2')
	#program.add_edge('p2is','p2i3')
	#program.add_edge('p2is','p2i4')
	#program.add_edge('p1i1','p2i4')
	#program.add_edge('p0i2','p2i4')
	#program.add_edge('p3i3','p2i4')

	#program.add_edge('p3is','p3i1')
	#program.add_edge('p3is','p3i2')
	#program.add_edge('p3is','p3i3')
	#program.add_edge('p3is','p3i4')
	#program.add_edge('p2i1','p3i4')
	#program.add_edge('p1i2','p3i4')
	#program.add_edge('p0i3','p3i4')

	# create machine for program
	machine = machine.Machine(program)

	# simulate
	simulator = Simulator()
	
	simulator.run(machine, program)
	# program gets changed, or could have record state in machine
	#simulator.run(program, machine)
	
	visual.outputPDF('test.pdf', machine, program)
	#visual.outputPDF('test.pdf', machine, record)
