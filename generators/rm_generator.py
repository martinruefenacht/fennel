#! /usr/bin/python3

from tasks import *
import networkx as nx
from sympy.ntheory import factorint
import math, sys
import matplotlib.pyplot as plt
import simulator, machine, visual, program, noise

from schedule_generator import *
from program_generator import *

from lbmachine import *
from logpmachine import * 

from collections import Counter
from itertools import * 
import operator
from functools import reduce


if __name__ == "__main__":
	size = int(sys.argv[1]) # N

	schedules = []
	schedules.extend(generate_factored(size))
	schedules.extend(generate_splits(size))
	schedules.extend(generate_merges(size))
	
	# user select
	print('Select schedule:')
	for idx, un in enumerate(schedules):
		print(idx,')', un)

	notDone = True
	while notDone:
		try:
			string = input('Select: ')

			if string[0] == 'e':
				sys.exit(0)
			else:
				sel = int(string)
				print('Selection ', sel)
				if sel < 0 or sel > len(schedules):
					raise ValueError
					
				notDone = False
		except SystemExit:
			print('Goodbye.')
			sys.exit(0)
		except Exception as err:
			print(err)
			print('Selection needs to be a number in the list.')


	# TODO select ordering of stages

	# blocking puts
	block_choice = input('Blocking [y]:')
	
	if block_choice == 'y':
		block = True
	else:
		block = False

	# program generator
	print('Schedule:', schedules[sel])
	p = schedule_to_program_generator(size, schedules[sel], block)


	# create machine
	m = LBPMachine(p, 1000, 0, 400)
	#m = LBMachine(p, 1400, 0)
	#m = LogPMachine(p, 200, 400, 300)
	#m = LogPMachineDuplex(p, 200, 400, 300)
	#m = LogPMachineSimplex(p, 200, 400, 300)

	#m.host_noise = noise.BetaPrimeNoise(2,3)
	#m.network_noise = noise.BetaPrimeNoise(2,3)

	v = visual.Visual()
	m.setVisual(v)

	# run program on machine
	m.run()
	print(m.getMaximumTime())

	v.savePDF('test.pdf')
