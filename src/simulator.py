#! /usr/bin/python3

import sys, parser, lbmachine, logpmachine, visual

if __name__ == "__main__":
	# parse program
	program = parser.parseGOAL(sys.argv[1])

	# create machine for program
	#machine = lbmachine.LBPMachine(program, 500, 0, 400)
	#machine = lbmachine.LBMachine(program, 700, 0)
	machine = logpmachine.LogPMachine(program)

	# set noise
	machine.host_noise = True
	machine.network_noise = True

	# set visual
	visual = visual.Visual()
	machine.setVisual(visual)

	machine.run()

	print(machine.procs)

	visual.savePDF('test.pdf')
