#! /usr/bin/python3

from tasks import *
import networkx as nx

import math, sys

import simulator, machine, visual

def recursive_doubling_program(size):
	program = nx.DiGraph()

	# all starting nodes
	for node in range(size):
		name = 'r'+str(node)+'l0c' 
		program.add_node(name, {'task':StartTask(name, node)})

	if (2**math.log2(int(size))) == int(size):
		# power of two
		
		stages = int(math.log2(int(size)))

		mask = 1
		for stage in range(stages):
			for node in range(size):
				# put destination
				peer = node ^ mask

				putname = 'r'+str(node)+'l'+str(stage+1)+'p'
				puttask = PutTask(putname, node, peer, 8)
				program.add_node(putname, {'task':puttask})

				comname = 'r'+str(node)+'l'+str(stage+1)+'c'
				comtask = ComputeTask(comname, node, delay=100)
				program.add_node(comname, {'task':comtask})

				prename = 'r'+str(node)+'l'+str(stage)+'c'
				peername = 'r'+str(peer)+'l'+str(stage+1)+'p'

				# this compute relies on previous compute
				program.add_edge(prename, comname)
				# put relies on last compute
				program.add_edge(prename, putname)
				# compute relies on other put
				program.add_edge(peername, comname)


			mask <<= 1

	return program

if __name__ == "__main__":
	p = recursive_doubling_program(int(sys.argv[1]))
	
	s = simulator.Simulator()

	m = machine.Machine(p)

	s.run(m, p)

	print(max(m.procs))

