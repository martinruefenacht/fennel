import sys

import simulator.generators.allreduce as allreduce
import simulator.models.lbmachine as lbmachine

if __name__ == '__main__':
	# argument check
	if len(sys.argv) is not 2:
		print('argument must be AllReduce size')
		print('python3 rm_draw N')
		sys.exit(1)

	# schedule selection
	process_count = int(sys.argv[1])
	
	schedules = allreduce.generate_factored(process_count)

	for idx, schedule in enumerate(schedules):
		print(idx, '\t', schedule)

	selection = int(input('Schedule choice: '))

	schedule = schedules[selection]
	print(schedule)

	# generate program
	program = allreduce.schedule_to_program_generator(schedule, False)
	
	machine = lbmachine.LBPMachine(program, 220, 0.4, 410)
	machine.run()

	print(machine.getMaximumTime())
	 
