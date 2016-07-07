#! /usr/bin/python3

import sys, parser, lbmachine, visual

if __name__ == "__main__":
	# parse program
	program = parser.parseGOAL(sys.argv[1])

	# create machine for program
	#machine = lbmachine.LBPMachine(program, 600, 0, 400)
	machine = lbmachine.LBMachine(program, 1000, 0)

	# set noise
	#machine.setHostNoise()
	#machine.setNetworkNoise()

	# set visual
	visual = visual.Visual()
	machine.setVisual(visual)

	machine.run()

	print(machine.procs)

	visual.savePDF('test.pdf')
