#! /usr/bin/python3

from heapq import *
from networkx import *
import cairo, sys
import numpy as np

from tasks import *
import parser, machine, simulator

if __name__ == "__main__":
	# parse program
	p = parser.parseGOAL(sys.argv[1])

	# simulate
	simulator = simulator.Simulator()
	
	times = []

	for sample in range(int(sys.argv[2])):
		# create machine for program
		m = machine.Machine(p, recording=False)
		
		simulator.run(m, p)

		times.append(max(m.procs))

	print(np.min(times), np.median(times), np.mean(times), np.max(times)) 
	
