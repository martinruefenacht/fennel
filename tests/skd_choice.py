import sys
import pickle
import generators.skdgen as skdgen
import core.schedule as schedule

def print_schedules(schedules):
	for idx, schedule in enumerate(schedules):
		print("{:5} {}".format(idx, schedule))

if __name__ == "__main__":
	# argument check
	if len(sys.argv) == 1:
		print("Command line error. ./skd_gen [s|selection] N")
		sys.exit(1)

	# parse process count
	show = (sys.argv[1] == 's')
	if not show:
		selection = int(sys.argv[1])
	process_count = int(sys.argv[2])

	# find all factored
	schedules = skdgen.generate_factored(process_count)

	if show:
		print_schedules(schedules)
	else:
		s = schedule.Schedule(process_count, schedules[selection])
		
		sys.stdout.buffer.write(pickle.dumps([s]))
