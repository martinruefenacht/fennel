#! /usr/bin/python3

from tasks import *
import networkx as nx
from sympy.ntheory import factorint
import math, sys
import matplotlib.pyplot as plt
import simulator, machine, visual, program, noise

from schedule import *

from lbmachine import *
from logpmachine import * 

from collections import Counter
from itertools import * 
import operator
from functools import reduce

from rm_generator import *

if __name__ == "__main__":
	size = int(sys.argv[1]) # N

	schedules = []
	schedules.extend(generate_factored(size))
	schedules.extend(generate_splits(size))

	block = False
	
	for schedule in schedules:
		# program generator
		print('Schedule:', schedule)
		p = schedule_to_program_generator(size, schedule, block)

		# create machine
		m = LBPMachine(p, 1000, 0, 400)

		# run program on machine
		m.run()
		print('>>>>', m.getMaximumTime())
