import sys
import pickle
import numpy as np
import timeit

import simulator.models.lbmachine as lbmachine
import simulator.generators.proggen as proggen
import simulator.core.noise as noise

if __name__ == '__main__':
	# parse schedule
	schedules = pickle.loads(sys.stdin.buffer.read())

	for schedule in schedules:
		print('schedule: ', schedule)
		
		# program generation
		program = proggen.schedule_to_program_generator(schedule, False, 1, True)

		

		
