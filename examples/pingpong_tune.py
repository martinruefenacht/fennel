import sys

import simulator.generators.p2p as p2p
import simulator.models.lbmachine as lbmachine
import simulator.core.noise as noise

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

if __name__ == "__main__":
	samples = []

	# program generation
	p = p2p.generate_pingpong(1, 10)

	# sampling
	for sample in range(int(sys.argv[1])):
		# machine creation
		m = lbmachine.LBPMachine(p, 1000, 0.4, 400)

		# noise configuration
		m.host_noise = noise.BetaPrimeNoise(2, 3)
		m.network_noise = noise.BetaPrimeNoise(2, 3, scale=0.475)

		m.run()
		
		samples.append(m.getMaximumTime())

	# analysis
	samples = np.array(samples)

	print('min: ', np.min(samples))
	print('median: ', np.median(samples))
	print('mean: ', np.mean(samples))
	print('q25: ', np.percentile(samples, 25))
	print('q75: ', np.percentile(samples, 75))
