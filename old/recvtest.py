import models.lbmachine as lbmachine
import core.program as program
import generators.allreduce as allreduce
import visual.visualizer as visualizer

import networkx as nx
import matplotlib.pyplot as plt

if __name__ == '__main__':
	# all to one pattern

	schedule = allreduce.Schedule(4, allreduce.generate_split(4, 4, 4)[0])

	prog = allreduce.schedule_to_program_generator(schedule)

	#prog.prt()

	#network = prog.convert_networkx()

	#pos = nx.spring_layout(network)
	#nx.draw_networkx_nodes(network, pos)
	#nx.draw_networkx_edges(network, pos, arrows=True)
	#plt.show()

	# TODO draw
	machine = lbmachine.LBPCMachine(4, 220, 0.4, 410, 100)

	vis = visualizer.Visual()

	machine.registerVisualContext(vis)

	machine.run(prog)
	vis.savePDF('test.pdf')
