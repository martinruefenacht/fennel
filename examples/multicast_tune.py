import sys

import simulator.generators.p2p as p2p
import simulator.models.lbmachine as lbmachine
import simulator.core.noise as noise

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

if __name__ == "__main__":
	if len(sys.argv) is not 3:
		print('command N samples')

	samples = []

	# program generation
	# 8B
	p = p2p.generate_multicast(8, int(sys.argv[1]))

	# sampling
	for sample in range(int(sys.argv[2])):
		# machine creation
		m = lbmachine.LBPMachine(p, 1000, 0.4, 360)

		# noise configuration
		#m.host_noise = noise.BetaPrimeNoise(2, 3, scale=0.075)
		#m.network_noise = noise.BetaPrimeNoise(2, 3, scale=1.075)

		m.run()
		
		samples.append(m.getMaximumTime())
		#samples.append(m.procs[0])

	# analysis
	samples = np.array(samples)

	print('min: ', np.min(samples))
	print('median: ', np.median(samples))
	print('mean: ', np.mean(samples))
	print('q25: ', np.percentile(samples, 25))
	print('q75: ', np.percentile(samples, 75))
