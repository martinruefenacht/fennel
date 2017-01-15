import simulator.core.program
import simulator.core.tasks as tasks

def program_7_nonoverlap():
	# set message size
	msgsize = 8

	# create program
	p = simulator.core.program.Program()

	# create start tasks
	for rid in range(7):
		name = 'r' + str(rid) + 's'
		p.addNode(name, tasks.StartTask(name, rid))

	# go through schedule
	# TODO
	# this is hardcoded

	# 3-2 elimination

	# 0 -> 1
	name = 'r0p0_1'
	p.addNode(name, tasks.PutTask(name, 0, 1, msgsize, False))
	p.addEdge('r0s', name)

	# 1 -> 0
	name = 'r1p0_0'
	p.addNode(name, tasks.PutTask(name, 1, 0, msgsize, False))
	p.addEdge('r1s', name)

	# 2 -> 1
	name = 'r2p0_1'
	p.addNode(name, tasks.PutTask(name, 2, 1, msgsize, False))
	p.addEdge('r2s', name)

	# reduce 0
	name = 'r0c0'
	p.addNode(name, tasks.ComputeTask(name, 0, delay=10))
	p.addEdge('r0s', name)
	p.addEdge('r1p0_0', name)

	# reduce 1
	name = 'r1c0'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r1s', name)
	p.addEdge('r0p0_1', name)

	# 0 -> 2
	name = 'r0p1_2'
	p.addNode(name, tasks.PutTask(name, 0, 2, msgsize, False))
	p.addEdge('r0c0', name)

	# reduce 1
	name = 'r1c1'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r2p0_1', name)
	p.addEdge('r1c0', name)

	# reduce 2
	name = 'r2c1'
	p.addNode(name, tasks.ComputeTask(name, 2, delay=10))
	p.addEdge('r2s', name)
	p.addEdge('r0p1_2', name)


	# 2-1 elimination
	# 3 -> 4
	name = 'r3p0_4'
	p.addNode(name, tasks.PutTask(name, 3, 4, msgsize, False))
	p.addEdge('r3s', name)
		
	# 5 -> 6
	name = 'r5p0_6'
	p.addNode(name, tasks.PutTask(name, 5, 6, msgsize, False))
	p.addEdge('r5s', name)

	# reduce 4
	name = 'r4c0'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r4s', name)
	p.addEdge('r3p0_4', name)

	# reduce 6
	name = 'r6c0'
	p.addNode(name, tasks.ComputeTask(name, 6, delay=10))
	p.addEdge('r6s', name)
	p.addEdge('r5p0_6', name)


	# a2 exchange for 2-1
	# 4 -> 6
	name = 'r4pz0_6'
	p.addNode(name, tasks.PutTask(name, 4, 6, msgsize, False))
	p.addEdge('r4c0', name)

	# 6 -> 4
	name = 'r6pz0_4'
	p.addNode(name, tasks.PutTask(name, 6, 4, msgsize, False))
	p.addEdge('r6c0', name)

	# reduce 4
	name = 'r4cz'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r4c0', name)
	p.addEdge('r6pz0_4', name)

	# reduce 6
	name = 'r6cz'
	p.addNode(name, tasks.ComputeTask(name, 6, delay=10))
	p.addEdge('r6c0', name)
	p.addEdge('r4pz0_6', name)

	# a2 schedule
	# 1 -> 4
	name = 'r1p10_4'
	p.addNode(name, tasks.PutTask(name, 1, 4, msgsize, False))
	p.addEdge('r1c1', name)

	# 2 -> 6
	name = 'r2p10_6'
	p.addNode(name, tasks.PutTask(name, 2, 6, msgsize, False))
	p.addEdge('r2c1', name)

	# 4 -> 1
	name = 'r4p10_1'
	p.addNode(name, tasks.PutTask(name, 4, 1, msgsize, False))
	p.addEdge('r4cz', name)

	# 6 -> 2
	name = 'r6p10_2'
	p.addNode(name, tasks.PutTask(name, 6, 2, msgsize, False))
	p.addEdge('r6cz', name)

	# reduce 1
	name = 'r1c10'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r4p10_1', name)
	p.addEdge('r1c1', name)

	# reduce 2
	name = 'r2c10'
	p.addNode(name, tasks.ComputeTask(name, 2, delay=10))
	p.addEdge('r6p10_2', name)
	p.addEdge('r2c1', name)

	# reduce 4
	name = 'r4c10'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r4c0', name)
	p.addEdge('r1p10_4', name)

	# reduce 6
	name = 'r6c10'
	p.addNode(name, tasks.ComputeTask(name, 6, delay=10))
	p.addEdge('r6c0', name)
	p.addEdge('r2p10_6', name)


	# 3-2 2-1 resolve
	# 1 -> 0
	name = 'r1p20_0'
	p.addNode(name, tasks.PutTask(name, 1, 0, msgsize, False))
	p.addEdge('r1c10', name)

	# 4 -> 3
	name = 'r4p20_3'
	p.addNode(name, tasks.PutTask(name, 4, 3, msgsize, False))
	p.addEdge('r4c10', name)

	# 6 -> 5
	name = 'r6p20_5'
	p.addNode(name, tasks.PutTask(name, 6, 5, msgsize, False))
	p.addEdge('r6c10', name)

	# reduce 0
	name = 'r1c30'
	p.addNode(name, tasks.ComputeTask(name, 0, delay=10))
	p.addEdge('r1p20_0', name)

	# reduce 3
	name = 'r3c30'
	p.addNode(name, tasks.ComputeTask(name, 3, delay=10))
	p.addEdge('r4p20_3', name)

	# reduce 5
	name = 'r5c30'
	p.addNode(name, tasks.ComputeTask(name, 5, delay=10))
	p.addEdge('r6p20_5', name)

	return p	

def program_7_overlap():
	# set message size
	msgsize = 8

	# create program
	p = simulator.core.program.Program()

	# create start tasks
	for rid in range(7):
		name = 'r' + str(rid) + 's'
		p.addNode(name, tasks.StartTask(name, rid))

	# 3-2 collapse	
	# 0 -> 1
	name = 'r0p0_1'
	p.addNode(name, tasks.PutTask(name, 0, 1, msgsize, False))
	p.addEdge('r0s', name)

	# 1 -> 0
	name = 'r1p0_0'
	p.addNode(name, tasks.PutTask(name, 1, 0, msgsize, False))
	p.addEdge('r1s', name)

	# 2 -> 1
	name = 'r2p0_1'
	p.addNode(name, tasks.PutTask(name, 2, 1, msgsize, False))
	p.addEdge('r2s', name)

	# reduce 0
	name = 'r0c0'
	p.addNode(name, tasks.ComputeTask(name, 0, delay=10))
	p.addEdge('r0s', name)
	p.addEdge('r1p0_0', name)

	# reduce 1
	name = 'r1c0'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r1s', name)
	p.addEdge('r0p0_1', name)

	# 0 -> 2
	name = 'r0p1_2'
	p.addNode(name, tasks.PutTask(name, 0, 2, msgsize, False))
	p.addEdge('r0c0', name)

	# reduce 1
	name = 'r1c1'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r2p0_1', name)
	p.addEdge('r1c0', name)

	# reduce 2
	name = 'r2c1'
	p.addNode(name, tasks.ComputeTask(name, 2, delay=10))
	p.addEdge('r2s', name)
	p.addEdge('r0p1_2', name)


	# a2 expand 
	# 3 -> 4
	name = 'r3p0_4'
	p.addNode(name, tasks.PutTask(name, 3, 4, msgsize, False))
	p.addEdge('r3s', name)

	# 4 -> 3
	name = 'r4p0_3'
	p.addNode(name, tasks.PutTask(name, 4, 3, msgsize, False))
	p.addEdge('r4s', name)

	# 5 -> 6
	name = 'r5p0_6'
	p.addNode(name, tasks.PutTask(name, 5, 6, msgsize, False))
	p.addEdge('r5s', name)

	# 6 -> 5
	name = 'r6p0_5'
	p.addNode(name, tasks.PutTask(name, 6, 5, msgsize, False))
	p.addEdge('r6s', name)

	# reduce 3
	name = 'r3c1'
	p.addNode(name, tasks.ComputeTask(name, 3, delay=10))
	p.addEdge('r4p0_3', name)
	p.addEdge('r3s', name)

	# reduce 4
	name = 'r4c1'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r3p0_4', name)
	p.addEdge('r4s', name)

	# reduce 5
	name = 'r5c1'
	p.addNode(name, tasks.ComputeTask(name, 5, delay=10))
	p.addEdge('r6p0_5', name)
	p.addEdge('r5s', name)

	# reduce 6
	name = 'r6c1'
	p.addNode(name, tasks.ComputeTask(name, 6, delay=10))
	p.addEdge('r5p0_6', name)
	p.addEdge('r6s', name)


	# 3-2 collapse #2
	# 1 -> 3
	name = 'r1p10_3'
	p.addNode(name, tasks.PutTask(name, 1, 3, msgsize, False))
	p.addEdge('r1c1', name)

	# 3 -> 1
	name = 'r3p10_1'
	p.addNode(name, tasks.PutTask(name, 3, 1, msgsize, False))
	p.addEdge('r3c1', name)

	# reduce 1
	name = 'r1c10'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r3p10_1', name)
	p.addEdge('r1c1', name)

	# reduce 3
	name = 'r3c10'
	p.addNode(name, tasks.ComputeTask(name, 3, delay=10))
	p.addEdge('r1p10_3', name)
	p.addEdge('r3c1', name)
	
	# 5 -> 3
	name = 'r5p15_3'
	p.addNode(name, tasks.PutTask(name, 5, 3, msgsize, False))
	p.addEdge('r5c1', name)

	# 1 -> 5
	name = 'r1p15_5'
	p.addNode(name, tasks.PutTask(name, 1, 5, msgsize, False))
	p.addEdge('r1c10', name)

	# reduce 3
	name = 'r3c15'
	p.addNode(name, tasks.ComputeTask(name, 3, delay=10))
	p.addEdge('r5p15_3', name)
	p.addEdge('r3c10', name)

	# reduce 5
	name = 'r5c15'
	p.addNode(name, tasks.ComputeTask(name, 5, delay=10))
	p.addEdge('r1p0_5', name)
	p.addEdge('r5c1', name)


	# seocnd 3-2 layer 2
	# 2 -> 4
	name = 'r2p10_4'
	p.addNode(name, tasks.PutTask(name, 2, 4, msgsize, False))
	p.addEdge('r2c1', name)

	# 4 -> 2
	name = 'r4p10_2'
	p.addNode(name, tasks.PutTask(name, 4, 2, msgsize, False))
	p.addEdge('r4c1', name)

	# reduce 2
	name = 'r2c10'
	p.addNode(name, tasks.ComputeTask(name, 2, delay=10))
	p.addEdge('r4p10_2', name)
	p.addEdge('r2c1', name)

	# reduce 4
	name = 'r4c10'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r2p10_4', name)
	p.addEdge('r4c1', name)
	
	# 6 -> 4
	name = 'r6p15_4'
	p.addNode(name, tasks.PutTask(name, 6, 4, msgsize, False))
	p.addEdge('r6c1', name)

	# 2 -> 6
	name = 'r2p15_6'
	p.addNode(name, tasks.PutTask(name, 2, 6, msgsize, False))
	p.addEdge('r2c10', name)

	# reduce 4
	name = 'r4c15'
	p.addNode(name, tasks.ComputeTask(name, 4, delay=10))
	p.addEdge('r6p15_4', name)
	p.addEdge('r4c10', name)

	# reduce 6
	name = 'r6c15'
	p.addNode(name, tasks.ComputeTask(name, 6, delay=10))
	p.addEdge('r2p0_6', name)
	p.addEdge('r6c1', name)


	# 3-2 expand
	
	# 4 -> 2
	name = 'r4p20_2'
	p.addNode(name, tasks.PutTask(name, 4, 2, msgsize, False))
	p.addEdge('r4c15', name)

	# 3 -> 1
	name = 'r3p20_1'
	p.addNode(name, tasks.PutTask(name, 3, 1, msgsize, False))
	p.addEdge('r3c15', name)

	# 1 -> 0
	name = 'r1p20_0'
	p.addNode(name, tasks.PutTask(name, 1, 0, msgsize, False))
	p.addEdge('r3p20_1', name)

	# reduce 2
	name = 'r2c20'
	p.addNode(name, tasks.ComputeTask(name, 2, delay=10))
	p.addEdge('r4p20_2', name)

	# reduce 1
	name = 'r1c20'
	p.addNode(name, tasks.ComputeTask(name, 1, delay=10))
	p.addEdge('r3p20_1', name)

	# reduce 0
	name = 'r0c20'
	p.addNode(name, tasks.ComputeTask(name, 0, delay=10))
	p.addEdge('r1p20_0', name)

	return p
