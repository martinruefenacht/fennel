from lbmachine import *
from tasks import *
from program import *
from noise import *
from visual import *

import numpy as np
import matplotlib.pyplot as plt

def generate_pingpong(msgsize):
	p = Program()

	p.dag.add_node('s0', {'task':StartTask('s0', 0)})
	p.dag.add_node('s1', {'task':StartTask('s1', 1)})
	
	p.dag.add_node('p0', {'task':PutTask('p0', 0, 1, msgsize)})
	p.dag.add_node('p1', {'task':PutTask('p1', 1, 0, msgsize)})

	p.dag.add_edge('s0', 'p0')
	p.dag.add_edge('s1', 'p1')
	p.dag.add_edge('p0', 'p1')

	return p

if __name__ == "__main__":
	d = []
	for log2 in range(3, 24):
		samples = []
		msgsize = 1 << log2

		p = generate_pingpong(msgsize)
		m = LBPMachine(p, 1000, 0.09, 400)
		m.host_noise = BetaPrimeNoise(2, 3)
		m.network_noise = BetaPrimeNoise(2, 3)

		for sample in range(10):
			m.run()
			
			samples.append(m.getMaximumTime()/1000)

			m.reset()

		d.append(samples)

	plt.boxplot(d)
	plt.yscale('log')

	plt.ylim(1,4000)
	plt.show()
	
