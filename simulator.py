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

	# create machine for program
	machine = machine.Machine(program)

	# simulate
	simulator = Simulator()
	
	simulator.run(machine, program)
	# program gets changed, or could have record state in machine
	#simulator.run(program, machine)
	
	visual.outputPDF('test.pdf', machine, program)
	#visual.outputPDF('test.pdf', machine, record)
