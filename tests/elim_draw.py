import sys, string

import generators.elimination as elimination
import models.lbmachine as lbmachine
import models.logpmachine as logpmachine
import visual.visualizer as visualizer
import generators.allreduce as allreduce

if __name__ == '__main__':
	# argument check
	if len(sys.argv) is not 2:
		print('argument must be AllReduce size')
		print('python3 rm_draw N')
		sys.exit(1)

	# schedule selection
	process_count = int(sys.argv[1])
	if process_count < 2:
		print('requirement 2 <= process count')
		sys.exit(2)
	
	schedules = allreduce.generate_factored(process_count)
	#schedules.extend(allreduce.generate_splits(process_count))
	#schedules.extend(allreduce.generate_merges(process_count))
	#schedules = []
	# TODO

	# select schedule
	print('Number of schedules: ', len(schedules))
	for idx, schedule in enumerate(schedules):
		print(idx, '\t', schedule)

	selection = input('Schedule choice (idx or idx-idx): ')

	if ' ' in selection:
		print('invalid format')
		sys.exit(3)

	elif '-' in selection:
		idxs = selection.split('-')
		
		select = []
		for idx in range(int(idxs[0]), int(idxs[1])+1):
			select.append(schedules[idx])
		
	else:
		idx = int(selection)
		select = [schedules[idx]]

	for order in select:
		print('Selected: ', order)
		
		schedule = allreduce.Schedule(process_count, order)
		# TODO

		# generate program
		program = allreduce.schedule_to_program_generator(schedule, False)
		# TODO

	# TODO HACK
	#process_count = 6
	#program = elimination.program_6_overlap()

	context = visualizer.Visual()
	
	machine = lbmachine.LBPCMachine(process_count, 450, 0.4, 100, 50)
	#machine = lbmachine.LBPMachine(process_count, 500, 0.4, 100)
	#machine = logpmachine.LogPMachine(process_count, 500, 100, 50)
	machine.registerVisualContext(context)
	machine.run(program)

	# draw
	#context.savePDF('rm_' + str(order) + '.pdf')
	context.savePDF('rm_elimination' + '.pdf')
