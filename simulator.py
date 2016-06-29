#! /usr/bin/python3

from heapq import *
from networkx import *
import cairo

from tasks import *

class Machine:
	def __init__(self, size):
		self.size = size

		self.alpha_p = 1500
		self.alpha_r = 1500
		self.beta = 30

		self.procs = [0] * self.size

class Simulator:
	def __init__(self):
		self.taskqueue = []

		# generate noise array
		#noisef = betaprime.rvs(2, 2, scale=25,size=1000)
		#self.noise = [int(round(i)) for i in noisef]

	def run(self, machine, program):
		# initiate program
		for nid, deg in program.in_degree_iter():
			if deg == 0:
				heappush(self.taskqueue, program.node[nid]['task'])

		# initiate visualization
		pdf = cairo.PDFSurface("test.pdf", 550, machine.size*36)
		ctx = cairo.Context(pdf)
		ctx.set_antialias(cairo.ANTIALIAS_GRAY)
		ctx.set_source_rgb(0,0,0)
		ctx.set_line_width(0.5)
		ctx.set_font_size(4)
	
		# proc lines
		for i in range(machine.size):
			ctx.move_to(10, 18+i*36)
			ctx.rel_line_to(500, 0)
			ctx.stroke()
		# time line
		ctx.move_to(10,2)
		ctx.rel_line_to(500, 0)
		ctx.stroke()

		for i in range(51):
			if i % 5 == 0:
				# draw number
				ctx.move_to(10+i*10, 10)
				ctx.show_text(str(i*100))
			ctx.move_to(10+i*10, 2)
			ctx.rel_line_to(0, 4)
			ctx.stroke()
		
		# process entire queue
		while self.taskqueue:
			# retrieve next global clock event
			task = heappop(self.taskqueue)

			# execute task
			time = task.execute(machine, ctx)

			# check for fail
			if time is None:
				# reschedule
				heappush(self.taskqueue, task)
				continue

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
			#print(machine.procs)
			#print()

		ctx.show_page()
		print(machine.procs)


if __name__ == "__main__":
	# parse YAML config

	# 
	machine = Machine(4)

	#
	# run N processes on machine with resources
	program = DiGraph()

	#program.add_node('p0is', {'task':StartTask('p0is', 0)})
	#program.add_node('p0i1', {'task':PutTask('p0i1', 0, 1, 8)})
	#program.add_node('p0i2', {'task':ComputeTask('p0i2', 0, 100)})

	#program.add_edge('p0is', 'p0i1')
	#program.add_edge('p0is', 'p0i2')

	# a2, a2
	program.add_node('p0is', {'task':StartTask('p0is', 0)})	
	program.add_node('p0i1', {'task':PutTask('p0i1', 0, 1, 8)})
	program.add_node('p0i2', {'task':ComputeTask('p0i2', 0, 100)})
	program.add_node('p0i3', {'task':PutTask('p0i3', 0, 2, 8)})
	program.add_node('p0i4', {'task':ComputeTask('p0i4', 0, 100)})
	
	program.add_node('p1is', {'task':StartTask('p1is', 1)})	
	program.add_node('p1i1', {'task':PutTask('p1i1', 1, 0, 8)})
	program.add_node('p1i2', {'task':ComputeTask('p1i2', 1, 100)})
	program.add_node('p1i3', {'task':PutTask('p1i3', 1, 3, 8)})
	program.add_node('p1i4', {'task':ComputeTask('p1i4', 1, 100)})

	program.add_node('p2is', {'task':StartTask('p2is', 2)})	
	program.add_node('p2i1', {'task':PutTask('p2i1', 2, 3, 8)})
	program.add_node('p2i2', {'task':ComputeTask('p2i2', 2, 100)})
	program.add_node('p2i3', {'task':PutTask('p2i3', 2, 0, 8)})
	program.add_node('p2i4', {'task':ComputeTask('p2i4', 2, 100)})

	program.add_node('p3is', {'task':StartTask('p3is', 3)})	
	program.add_node('p3i1', {'task':PutTask('p3i1', 3, 2, 8)})
	program.add_node('p3i2', {'task':ComputeTask('p3i2', 3, 100)})
	program.add_node('p3i3', {'task':PutTask('p3i3', 3, 1, 8)})
	program.add_node('p3i4', {'task':ComputeTask('p3i4', 3, 100)})

	program.add_edge('p0is','p0i1')
	program.add_edge('p0is','p0i2')
	program.add_edge('p1i1','p0i2')
	program.add_edge('p0i2','p0i3')
	program.add_edge('p0i2','p0i4')
	program.add_edge('p2i3','p0i4')
		
	program.add_edge('p1is','p1i1')
	program.add_edge('p1is','p1i2')
	program.add_edge('p0i1','p1i2')
	program.add_edge('p1i2','p1i3')
	program.add_edge('p1i2','p1i4')
	program.add_edge('p3i3','p1i4')

	program.add_edge('p2is','p2i1')
	program.add_edge('p2is','p2i2')
	program.add_edge('p3i1','p2i2')
	program.add_edge('p2i2','p2i3')
	program.add_edge('p2i2','p2i4')
	program.add_edge('p0i3','p2i4')

	program.add_edge('p3is','p3i1')
	program.add_edge('p3is','p3i2')
	program.add_edge('p2i1','p3i2')
	program.add_edge('p3i2','p3i3')
	program.add_edge('p3i2','p3i4')
	program.add_edge('p1i3','p3i4')
	
	
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

	# simulate
	simulator = Simulator()
	
	simulator.run(machine, program)
