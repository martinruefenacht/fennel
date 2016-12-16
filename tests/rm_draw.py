import sys

import simulator.generators.allreduce as allreduce
import simulator.models.lbmachine as lbmachine
import simulator.visual.visualizer as visualizer

if __name__ == '__main__':
	# argument check
	if len(sys.argv) is not 2:
		print('argument must be AllReduce size')
		print('python3 rm_draw N')
		sys.exit(1)

	# schedule selection
	process_count = int(sys.argv[1])
	
	schedules = allreduce.generate_factored(process_count)
	schedules.extend(allreduce.generate_splits(process_count))
	schedules.extend(allreduce.generate_merges(process_count))

	print('Number of schedules: ', len(schedules))
	for idx, schedule in enumerate(schedules):
		print(idx, '\t', schedule)

	selection = int(input('Schedule choice: '))

	schedule = allreduce.Schedule(process_count, schedules[selection])

	# generate program
	program = allreduce.schedule_to_program_generator(schedule, False)

	context = visualizer.Visual()
	
	machine = lbmachine.LBPMachine(process_count, 220, 0.4, 410)
	machine.registerVisualContext(context)
	machine.run(program)

	# draw
	context.savePDF('output.pdf')		
