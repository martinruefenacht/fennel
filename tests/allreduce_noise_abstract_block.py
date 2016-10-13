import simulator.core.schedule as schedule
import simulator.generators.skdgen as skdgen
import simulator.core.noise as noise
import simulator.generators.proggen as proggen
import simulator.models.lbmachine as lbmachine

import matplotlib.pyplot as plt

import timeit, sys
import numpy as np

if __name__ == "__main__":
	data = []
	block_size = 10

	for power in range(1, 7):
		process_count = 2 << power
		print(process_count)

		skd = schedule.Schedule(process_count, skdgen.generate_factored(process_count)[0])
		program = proggen.schedule_to_program_generator(skd, False, block_size)

		time_start = timeit.default_timer()

		samples = []
		for sample in range(int(sys.argv[1])):
			machine = lbmachine.LBPMachine(program, 655, 0.4, 410)
			
			machine.host_noise = noise.InvGaussNoise(0.6, 0, 50)
			machine.network_noise = noise.GammaNoise(15.85, 0, 3.6)

			machine.run()

			samples.append(machine.getMaximumTime()/float(block_size))

		time_end = timeit.default_timer()

		samples = np.array(samples)
		samples /= 1000.0
		data.append(samples)
		print('min: ', np.min(samples))
		print('median: ', np.median(samples))
		print('mean: ', np.mean(samples))
		print('q25: ', np.percentile(samples, 25))
		print('q75: ', np.percentile(samples, 75))
		print()
		print('execution_time: ', round(time_end-time_start, 3))
		print()

	# graph
	plt.boxplot(data)
	plt.show()	
