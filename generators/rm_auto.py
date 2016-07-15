#! /usr/bin/python3

import math, sys
import simulator, machine, visual, program, noise

from schedule import *

from lbmachine import *
from logpmachine import * 

from rm_generator import *

if __name__ == "__main__":
	mins = []

	for size in range(2, int(sys.argv[1])):
		schedules = []
		schedules.extend(generate_factored(size))
		schedules.extend(generate_splits(size))

		block = False

		min_schedule = None
		min_time = math.inf
		
		for schedule in schedules:
			# program generator
			p = schedule_to_program_generator(size, schedule, block)

			# create machine
			m = LBPMachine(p, 1000, 0, 400)

			# run program on machine
			m.run()

			time = m.getMaximumTime()

			if time < min_time:
				min_time = time
				min_schedule = schedule

		mins.append((size, min_time,min_schedule))

	for size, time, schedule  in mins:
		print(size, time, schedule)
		
	
