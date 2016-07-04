#! /usr/bin/python3

import sys, parser, machine

if __name__ == "__main__":
	# parse program
	program = parser.parseGOAL(sys.argv[1])

	# create machine for program
	machine = machine.Machine(program, recording=True)

	machine.run()

	print(machine.procs)
	
	#visual.outputPDF('test.pdf', machine, program)
	#visual.outputPDF('test.pdf', machine, record)
