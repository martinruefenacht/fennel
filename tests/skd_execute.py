import sys
import pickle
import numpy as np

import simulator.models.lbmachine as lbmachine
import simulator.generators.proggen as proggen
import simulator.core.noise as noise

if __name__ == '__main__':
	if len(sys.argv) is not 3:
		print('generator | command samples noise')

	# parse schedule
	schedule = pickle.loads(sys.stdin.buffer.read())

	# program generation
	program = proggen.schedule_to_program_generator(schedule, False)

	# sampling
	samples = []
	for sidx in range(int(sys.argv[1])):
		# create machine
		machine = lbmachine.LBPMachine(program, 1000, 0.4, 400)

		if sys.argv[2] is 'n':
			machine.host_noise = noise.BetaPrimeNoise(2, 3)
			machine.network_noise = noise.BetaPrimeNoise(2, 3, scale=0.25)

		# heavy!
		machine.run()

		# sample
		samples.append(machine.getMaximumTime())

	# statistics
	samples = np.array(samples)
	print('min: ', np.min(samples))
	print('median: ', np.median(samples))
	print('mean: ', np.mean(samples))
	print('q25: ', np.percentile(samples, 25))
	print('q75: ', np.percentile(samples, 75))
	
