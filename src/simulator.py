#! /usr/bin/python3

import sys, parser, lbmachine

if __name__ == "__main__":
	# parse program
	program = parser.parseGOAL(sys.argv[1])

	# create machine for program
	machine = lbmachine.LBMachine(program, 750, 0)

	# set noise
	#machine.setHostNoise()
	#machine.setNetworkNoise()

	# set visual
	#machine.setVisual(visual)

	machine.run()

	print(machine.procs)

	#visual.outputPDF('test.pdf', machine, program)
