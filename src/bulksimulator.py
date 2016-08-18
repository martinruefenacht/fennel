#! /usr/bin/python3

import sys

from tasks import *
import parser, machine
import lbmachine

if __name__ == "__main__":
	# parse program
	p = parser.parseGOAL(sys.argv[1])

	# simulate
	times = []

	for sample in range(int(sys.argv[2])):
		# create machine for program
		#om = machine.Machine(p, recording=False)
		m = lbmachine.LBMachine(p, 700, 0)

		m.run()	

		times.append(max(m.procs))

	print(np.min(times), np.median(times), np.mean(times), np.max(times)) 
	
