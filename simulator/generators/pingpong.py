import program

def generate_pingpong(msgsize):
	prog = program.Program()

	prog.addNode('s0', StartTask('s0', 0))
	prog.addNode('s1', StartTask('s1', 1))
	
	prog.addNode('p0', PutTask('p0', 0, 1, msgsize))
	prog.addNode('p1', PutTask('p1', 1, 0, msgsize))

	prog.addEdge('s0', 'p0')
	prog.addEdge('s1', 'p1')
	prog.addEdge('p0', 'p1')

	return prog
