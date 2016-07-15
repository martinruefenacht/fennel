#! /usr/bin/python3

from tasks import *
import networkx as nx
from sympy.ntheory import factorint
import math, sys
import matplotlib.pyplot as plt
import simulator, machine, visual, program, noise

from schedule import *

from lbmachine import *
from logpmachine import * 

from collections import Counter
from itertools import * 
import operator
from functools import reduce

def schedule_to_program_generator(size, schedule, block):
	msgsize = 8 
	p = program.Program()

	positions = {}

	# create start tasks
	for rid in range(size):
		name = 'r' + str(rid) + 'c0'
		p.dag.add_node(name, {'task':StartTask(name, rid)})
		positions[name] = (rid, 0)

	# run through schedule
	split_stack = []
	stage_mask = 1
	wids = {}
	#rids = {}
	
	for scount, stage in enumerate(schedule):
		# stage id
		sid = scount + 1

		# if factor
		if stage.stype is StageType.factor:
			# decode stage
			factor = stage.arg1

			# 
			group_size = factor * stage_mask
			
			# for every node
			for rid in range(size):
				# working id
				if len(wids) == 0:
					wid = rid
				else:
					wid = wids[rid]

				# check for activeness
				if wid < 0:
					continue
				
				#
				group = (wid // group_size) * group_size

				# compute
				name = 'r' + str(rid) + 'c' + str(sid)
				p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
				positions[name] = (rid, -sid)
				
				# compute is dependent on previous compute
				p.dag.add_edge('r' + str(rid) + 'c' + str(sid-1), name)

				# for each peer
				for idx in range(factor-1):
					# staggered multicast
					mask = (idx + 1) * stage_mask
					offset = (wid + mask) % group_size
					pwid = group + offset

					# convert wid to rid
					# TODO can this be stored with rids?
					# THIS ONLY WORKS WITH A SPLIT
					if len(split_stack) > 0:
						cthreshold, cbase = split_stack[len(split_stack)-1]
						prid = pwid + cthreshold // cbase * (cbase - 1)
						if prid < cthreshold:
							prid = (pwid * cbase) + (cbase - 1)
					else:
						prid = pwid
						
					# create put for peer
					pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
					ptask = PutTask(pname, rid, prid, msgsize, block)
					p.dag.add_node(pname, {'task':ptask})
					positions[pname] = (rid+0.1+idx/(factor-1), -sid+0.2)
					
					# depends on previous compute
					p.dag.add_edge('r' + str(rid) + 'c' + str(sid-1), pname)
					# add dependency for all follow computes
					p.dag.add_edge(pname, 'r' + str(prid) + 'c' + str(sid)) 

			# increment mask
			stage_mask *= factor

		elif stage.stype is StageType.split:
			# decode stage
			threshold = stage.arg1
			base = stage.arg2

			# insert into stack
			split_stack.append((threshold, base))

			# sensical names
			groups = threshold/base
			group_size = base
			group_uppermost = base - 1

			# for all procs
			for rid in range(size):

				# if in collapse region
				if rid < threshold:

					# if not leader of group
					if rid % group_size != group_uppermost:
						# assign wid
						wid = -1 - rid

						# send to uppermost in group
						group_leader = (rid // group_size) * group_size + group_uppermost

						# construct put
						name = 'r' + str(rid) + 'p' + str(sid)
						p.dag.add_node(name, {'task':PutTask(name, rid, group_leader, msgsize, block)})
						p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), name)
						positions[name] = (rid, -sid+0.1)
	
					# if leader of group
					else:
						# assign working id
						wid = rid // group_size

						# construct compute
						name = 'r'+str(rid)+'c'+str(sid)
						p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
						p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), name)
						positions[name] = (rid, -sid)

						# add dependencies
						for idx in range(group_uppermost):
							pid = (rid // group_size) * group_size + idx
							pname = 'r' + str(pid) + 'p' + str(sid)
							p.dag.add_edge(pname, name)							

				# above collapse region
				else:
					# assign wid
					wid = rid - int(groups * group_uppermost)

					# create proxy
					name = 'r' + str(rid) + 'c' + str(sid)
					p.dag.add_node(name, {'task':ProxyTask(name, rid)})
					p.dag.add_edge('r' + str(rid) + 'c' + str(sid-1), name)
					positions[name] = (rid, -sid)

				# insert rid & wid into translation dict
				wids[rid] = wid
				#rids[wid] = rid

		elif stage.stype is StageType.invsplit:
			# decode stage
			threshold = stage.arg1
			base = stage.arg2

			# sensical names
			group_size = base
			group_uppermost = base - 1
			
			# for all procs
			for rid in range(size):
				wid = wids[rid]
				
				# if in collapse region
				if rid < threshold:
					
					# if leader in group
					if rid % group_size == group_uppermost:
						for offset in range(group_uppermost):
							prid = wid * group_size + offset

							name = 'r' + str(rid) + 'p' + str(sid) + '_' + str(offset)
							p.dag.add_node(name, {'task':PutTask(name, rid, prid, msgsize, block)})
							p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), name)
							positions[name] = (rid - (group_uppermost-offset)/group_size, -sid)

							p.dag.add_edge(name, 'r'+str(prid)+'c'+str(sid))

					# if not leader
					else:
						# construct compute
						name = 'r' + str(rid) + 'c' + str(sid)
						p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
						positions[name] = (rid, -sid-1)

	# testing
	#nx.draw_networkx(p.dag, pos=positions)
	#plt.show()		

	return p

if __name__ == "__main__":
	size = int(sys.argv[1]) # N

	schedules = []
	schedules.extend(generate_factored(size))
	schedules.extend(generate_splits(size))
	
	# user select
	print('Select schedule:')
	for idx, un in enumerate(schedules):
		print(idx,')', un)

	notDone = True
	while notDone:
		try:
			string = input('Select: ')

			if string[0] == 'e':
				sys.exit(0)
			else:
				sel = int(string)
				print('Selection ', sel)
				if sel < 0 or sel > len(schedules):
					raise ValueError
					
				notDone = False
		except SystemExit:
			print('Goodbye.')
			sys.exit(0)
		except Exception as err:
			print(err)
			print('Selection needs to be a number in the list.')


	# TODO select ordering of stages

	# blocking puts
	block_choice = input('Blocking [y]:')
	
	if block_choice == 'y':
		block = True
	else:
		block = False

	# program generator
	print('Schedule:', schedules[sel])
	p = schedule_to_program_generator(size, schedules[sel], block)


	# create machine
	m = LBPMachine(p, 1000, 0, 400)
	#m = LBMachine(p, 1400, 0)
	#m = LogPMachine(p, 200, 400, 300)
	#m = LogPMachineDuplex(p, 200, 400, 300)
	#m = LogPMachineSimplex(p, 200, 400, 300)

	#m.host_noise = noise.BetaPrimeNoise(2,3)
	#m.network_noise = noise.BetaPrimeNoise(2,3)

	v = visual.Visual()
	m.setVisual(v)

	# run program on machine
	m.run()
	print(m.getMaximumTime())

	v.savePDF('test.pdf')
