import simulator.core.program as program
import simulator.core.tasks as tasks

def generate_multicast(msgsize, count):
	prog = program.Program()

	# start nodes
	for cidx in range(count):
		prog.addNode('s'+str(cidx), tasks.StartTask('s'+str(cidx), cidx))

	# puts
	for cidx in range(1, count):
		prog.addNode('p0_'+str(cidx), tasks.PutTask('p0_'+str(cidx), 0, cidx, msgsize))
		prog.addEdge('s0', 'p0_'+str(cidx))

	return prog

def generate_pingpong(msgsize, count):
	prog = program.Program()

	prog.addNode('s0', tasks.StartTask('s0', 0))
	prog.addNode('s1', tasks.StartTask('s1', 1))

	prog.addNode('p0_0', tasks.PutTask('p0_0', 0, 1, msgsize))
	prog.addNode('p1_0', tasks.PutTask('p1_0', 1, 0, msgsize))

	prog.addEdge('s0', 'p0_0')
	prog.addEdge('s1', 'p1_0')

	# ping
	prog.addEdge('p0_0', 'p1_0')

	for cidx in range(1, count):
		prog.addNode('p0_'+str(cidx), tasks.PutTask('p0_'+str(cidx), 0, 1, msgsize))
		prog.addNode('p1_'+str(cidx), tasks.PutTask('p1_'+str(cidx), 1, 0, msgsize))

		prog.addEdge('p0_'+str(cidx-1), 'p0_'+str(cidx))
		prog.addEdge('p1_'+str(cidx-1), 'p1_'+str(cidx))

		# pong
		prog.addEdge('p1_'+str(cidx-1), 'p0_'+str(cidx))
		
		# ping
		prog.addEdge('p0_'+str(cidx), 'p1_'+str(cidx))

	return prog
