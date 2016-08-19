
#if __name__ == "__main__":
#	d = []
#	for log2 in range(3, 24):
#		samples = []
#		msgsize = 1 << log2
#
#		p = generate_pingpong(msgsize)
#		m = LBPMachine(p, 1000, 0.09, 400)
#		m.host_noise = BetaPrimeNoise(2, 3)
#		m.network_noise = BetaPrimeNoise(2, 3)
#
#		for sample in range(10):
#			m.run()
#			
#			samples.append(m.getMaximumTime()/1000)
#
#			m.reset()
#
#		d.append(samples)
#
#	plt.boxplot(d)
#	plt.yscale('log')
#
#	plt.ylim(1,4000)
#	plt.show()
	
