#! /usr/bin/python3

from tasks import *
import networkx as nx
from sympy.ntheory import factorint
import math, sys
import matplotlib.pyplot as plt
import simulator, machine, visual, program, noise

from lbmachine import *
from logpmachine import * 

from collections import Counter
from itertools import * 
import operator
from functools import reduce

def schedule_to_program_generator(size, schedule, block):
	msgsize = 8 
	p = program.Program()

	positions = {}

	# create start tasks
	stage_mask = 1
	for node in range(size):
		name = 'r' + str(node) + 'c0'
		p.dag.add_node(name, {'task':StartTask(name, node)})
		positions[name] = (node, 0)

	# run through schedule
	for stage, factor in enumerate(schedule):
		sid = stage + 1
		base = factor * stage_mask
		
		# for every node
		for node in range(size):
			group = (node // base) * base

			# create compute
			cname = 'r'+str(node)+'c'+str(sid)
			ctask = ComputeTask(cname, node, delay=10)
			p.dag.add_node(cname, {'task':ctask})
			positions[cname] = (node, -sid)
			
			# compute is dependent on previous compute
			p.dag.add_edge('r'+str(node)+'c'+str(sid-1), cname)

			# for each peer
			for idx in range(factor-1):
				mask = (idx + 1) * stage_mask
				offset = (node + mask) % base
				peer = group + offset
				
				# create put for peer
				pname = 'r'+str(node)+'p'+str(sid)+str(idx)
				ptask = PutTask(pname, node, peer, msgsize, block)
				p.dag.add_node(pname, {'task':ptask})
				positions[pname] = (node+0.1+idx/(factor-1), -sid+0.2)
				
				# depends on previous compute
				p.dag.add_edge('r'+str(node)+'c'+str(sid-1), pname)
   				# add dependency for all follow computes
				p.dag.add_edge(pname, 'r'+str(peer)+'c'+str(sid)) 

		# increment mask
		stage_mask *= factor

	# testing: draw graph
	#nx.draw_networkx(p.dag, pos=positions)
	#plt.show()

	return p

if __name__ == "__main__":
	size = int(sys.argv[1]) # N
	
	# factor size
	factors = factorint(size)
	prime_schedule = [key for key, count in factors.items() for c in range(count)]

	# combine schedules
	unique = []
	stack = []
	stack.append(tuple(prime_schedule))
	while stack:
		# retrieve item
		item = stack.pop()

		# check if done
		if tuple(item) not in unique:
			# add to unique set
			unique.append(tuple(item))

			# check for combinations
			if len(item) is not 1:
				# create pairings
				pairs = set(combinations(item, 2))

				for pair in pairs:
					# subtract pair
					diff_set = Counter(item) - Counter(pair)

					# calculate product of pair
					value = reduce(operator.mul, pair)

					# combine into new set
					combine_set = diff_set + Counter([value])

					# push to stack
					stack.append(tuple(combine_set.elements()))
	
	# user select
	print('Select schedule:')
	for idx, un in enumerate(unique):
		print(idx,')', un)
	sel = int(input('Select: '))

	if len(sys.argv) == 3:
		block = True if sys.argv[2] == 'block' else False
	else:
		block = False

	# TODO select ordering of stages

	# program generator
	print('Schedule:', unique[sel])
	p = schedule_to_program_generator(size, unique[sel], block)


	# create machine
	#m = LBPMachine(p, 1000, 0, 400)
	#m = LBMachine(p, 1400, 0)
	m = LogPMachine(p)

	#m.host_noise = noise.BetaPrimeNoise(2,3)
	#m.network_noise = noise.BetaPrimeNoise(2,3)

	v = visual.Visual()
	m.setVisual(v)

	# run program on machine
	m.run()
	print(m.getMaximumTime())

	v.savePDF('test.pdf')
