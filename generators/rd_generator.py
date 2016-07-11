#! /usr/bin/python3

from tasks import *
import networkx as nx

import math, sys
import matplotlib.pyplot as plt

import simulator, lbmachine, visual, program

def recursive_doubling_program(size):
	msgsize = 8
	p = program.Program()

	# all starting nodes
	for node in range(size):
		name = 'r'+str(node)+'s'
		p.dag.add_node(name, {'task':StartTask(name, node)})
	
	stages = math.floor(math.log2(int(size)))
	pof2 = 2**stages
	remainder = size - pof2

	mapping = []

	if pof2 != int(size):
		# collapse phase
		for proc in range(size):
			if proc < 2*remainder:
				if proc % 2 == 0:
					# send to proc+1
					name = 'r'+str(proc)+'c' 
					task = PutTask(name, proc, proc+1, msgsize)
					p.dag.add_node(name, {'task':task})
					p.dag.add_edge('r'+str(proc)+'s', name)
					
					mapping.append(-1)
				else:
					# create compute node
					name = 'r'+str(proc)+'c'
					task = ComputeTask(name, proc, delay=100)
					p.dag.add_node(name, {'task':task})
					p.dag.add_edge('r'+str(proc)+'s', name)

					# create edge
					peer = 'r'+str(proc-1)+'c'
					p.dag.add_edge(peer, name)

					# create proxy for RD
					proxyname = 'r'+str(proc)+'d0'
					proxytask = ProxyTask(proxyname, proc)
					
					p.dag.add_node(proxyname, {'task':proxytask})
					p.dag.add_edge(name, proxyname)

					mapping.append(proc // 2)
			else:
				# create proxy node
				proxyname = 'r'+str(proc)+'d0'
				proxytask = ProxyTask(proxyname, proc)

				p.dag.add_node(proxyname, {'task':proxytask})
				p.dag.add_edge('r'+str(proc)+'s', proxyname)

				mapping.append(proc - remainder)
	else:
		for proc in range(size):
			# create proxy
			name = 'r'+str(proc)+'d0'
			task = ProxyTask(name, proc)
			p.dag.add_node(name, {'task':task})
			p.dag.add_edge('r'+str(proc)+'s', 'r'+str(proc)+'d0')
		
			mapping.append(proc)

	# recursive doubling for remaining
	mask = 1
	for stage in range(stages):
		for rproc in range(size):
			if mapping[rproc] != -1:
				proc = mapping[rproc]

				# put destination
				peer = proc ^ mask

				# virtual -> real
				if peer < remainder:
					rpeer = peer * 2 + 1
				else:
					rpeer = peer + remainder

				# create nodes
				pname = 'r'+str(rproc)+'p'+str(stage+1)
				ptask = PutTask(pname, rproc, rpeer, 8)
				p.dag.add_node(pname, {'task':ptask})
				
				cname = 'r'+str(rproc)+'d'+str(stage+1)
				ctask = ComputeTask(cname, rproc, delay=100)
				p.dag.add_node(cname, {'task':ctask})

				# compute dependent on previous compute
				p.dag.add_edge('r'+str(rproc)+'d'+str(stage), cname)
				# put dependent on previous compute
				p.dag.add_edge('r'+str(rproc)+'d'+str(stage), pname)
				# compute dependent on peer put
				p.dag.add_edge('r'+str(rpeer)+'p'+str(stage+1), cname)

		# increment mask
		mask <<= 1

	if pof2 != int(size):
		# expand phase
		for proc in range(size):
			if proc < 2*remainder:
				if proc % 2 == 1:
					# send to proc-1
					name = 'r'+str(proc)+'e' 
					task = PutTask(name, proc, proc-1, msgsize)
					p.add_node(name, {'task':task})
					p.add_edge(name, 'r'+str(proc-1)+'e')
					p.add_edge('r'+str(proc)+'d'+str(stages), name)

				else:
					# compute/replace
					name = 'r'+str(proc)+'e'
					task = ProxyTask(name, proc)
					p.add_node(name, {'task':task})
					
	return p

if __name__ == "__main__":
	p = recursive_doubling_program(int(sys.argv[1]))


	#if len(sys.argv) == 3:
	#	m = lbmachine.LBMachine(p, 700, 0)
	#else:
	#	m = lbmachine.LBPMachine(p, 500, 0, 400)

	v = visual.Visual()
	
	m.setVisual(v)
	m.run()

	print(m.getMaxTime())

	v.savePDF('test.pdf')

