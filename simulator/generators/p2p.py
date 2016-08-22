import simulator.core.program as program
import simulator.core.tasks as tasks

def generate_pingpong(msgsize):
	prog = program.Program()

	prog.addNode('s0', tasks.StartTask('s0', 0))
	prog.addNode('s1', tasks.StartTask('s1', 1))
	
	prog.addNode('p0', tasks.PutTask('p0', 0, 1, msgsize))
	prog.addNode('p1', tasks.PutTask('p1', 1, 0, msgsize))

	prog.addEdge('s0', 'p0')
	prog.addEdge('s1', 'p1')
	prog.addEdge('p0', 'p1')

	return prog
