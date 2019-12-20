import simulator.generators.skdgen as skdgen
import simulator.generators.proggen as proggen
import simulator.models.lbmachine as lbmachine 

import sys

if __name__ == '__main__':
	# parse process count
	process_count = int(sys.argv[1])

	# generate all possible factored schedules
	schedules = skdgen.generate_factored(process_count)

	# evaluate each schedule
	for schedule in schedules:
		# generate program from schedule
		program = proggen.schedule_to_program_generator(process_count, schedule, False)
		
		# create machine
		machine = lbmachine.LBPMachine(program, 1000, 0, 400)

		# execute program
		machine.run()

		# record metric
		print('{}'.format(schedule) + ' - ' + '{}'.format(machine.getMaximumTime()))

		
