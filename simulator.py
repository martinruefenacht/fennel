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
				heappush(self.taskqueue, (0, nid))

		# process entire queue
		while self.taskqueue:
			# retrieve next global clock event
			time_in, nid = heappop(self.taskqueue)

			# retrieve task from program
			#task = program.getTask(nid)
			task = program.node[nid]['task']

			# execute task
			success, time_out = task.execute(machine, time_in)

			# check success
			if success:
				successors = machine.markComplete(program, nid, time_out)

				# push all available successors to queue
				for successor in successors:
					heappush(self.taskqueue, successor)
			else:
				# reinsert into task queue
				heappush(self.taskqueue, (time_out, nid))

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
