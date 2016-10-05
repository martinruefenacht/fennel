import sys
import pickle
import numpy as np
import timeit

import simulator.models.lbmachine as lbmachine
import simulator.generators.proggen as proggen
import simulator.core.noise as noise

if __name__ == '__main__':
	if len(sys.argv) is not 3:
		print('generator | command samples noise')

	# parse schedule
	schedules = pickle.loads(sys.stdin.buffer.read())

	for schedule in schedules:
		print('schedule: ', schedule)
		print('samples: ', int(sys.argv[1]))
		
		# program generation
		program = proggen.schedule_to_program_generator(schedule, False)

		# sampling
		start = timeit.default_timer()
		samples = []
		for sidx in range(int(sys.argv[1])):
			# create machine
			machine = lbmachine.LBPMachine(program, 1000, 0.4, 400)

			if len(sys.argv) == 3 and sys.argv[2] is 'n':
				machine.host_noise = noise.BetaPrimeNoise(2, 3)
				machine.network_noise = noise.BetaPrimeNoise(2, 3, scale=0.25)

			# heavy!
			machine.run()

			# sample
			samples.append(machine.getMaximumTime())
		end = timeit.default_timer()

		# statistics
		samples = np.array(samples)
		print('execution_time: ', round(end-start, 3))
		print('min: ', np.min(samples)/1000.0)
		print('median: ', np.median(samples)/1000.0)
		print('mean: ', np.mean(samples)/1000.0)
		print('q25: ', np.percentile(samples, 25)/1000.0)
		print('q75: ', np.percentile(samples, 75)/1000.0)
		
