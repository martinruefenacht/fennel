from schedule_generator import *
from program_generator import *
from lbmachine import * 

if __name__ == '__main__':
	# parse process count
	process_count = int(sys.argv[1])

	# generate all possible factored schedules
	schedules = generate_factored(process_count)

	# evaluate each schedule
	for schedule in schedules:
		# generate program from schedule
		program = schedule_to_program_generator(process_count, schedule, False)
		
		# create machine
		machine = LBPMachine(program, 1000, 0, 400)

		# execute program
		machine.run()

		# record metric
		print('%100s - %10i' % (schedule, machine.getMaximumTime()))

		
