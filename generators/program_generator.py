#! /usr/bin/python3

from stage import *
from schedule_generator import *
from program import *
from tasks import *

import networkx as nx
import matplotlib.pyplot as plt

def generate_program(schedule):
	pass	

def schedule_to_program_generator(size, schedule, block):
	msgsize = 8 
	p = Program()

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
							positions[name] = (rid - offset/group_size, -sid)

							p.dag.add_edge(name, 'r'+str(prid)+'c'+str(sid))

					# if not leader
					else:
						# construct compute
						name = 'r' + str(rid) + 'c' + str(sid)
						p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
						positions[name] = (rid, -sid-0.1)
		
		elif stage.stype is StageType.merge:
			# decode
			merge_threshold = stage.arg1
			groups = stage.arg2

			factor = stage.arg3
			group_size = stage.arg3 * stage_mask

			# for all procs
			for rid in range(size):

				# if in merge region
				if rid < merge_threshold:
					wids[rid] = -1 -rid
					
					# which group to
					group = rid % groups
					
					# group base rid
					group_first = merge_threshold + group * group_size

					# for each in group
					for idx in range(group_size):
						prid = group_first + idx

						# put
						pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
						p.dag.add_node(pname, {'task':PutTask(pname, rid, prid, msgsize, block)})
						p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), pname)
						p.dag.add_edge(pname, 'r' + str(prid) + 'c' + str(sid))
						positions[pname] = (rid+idx/group_size, -sid+0.2)

				else:
					wid = rid - merge_threshold
					wids[rid] = wid
					
					# normal factor exchange
					group = (wid // group_size) * group_size

					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
					p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), name)
					positions[name] = (rid, -sid)
					
					# for each group peer
					for idx in range(factor-1):
						# staggered multicast
						mask = (idx + 1) * stage_mask
						offset = (wid + mask) % group_size
						pwid = group + offset
						
						# convert wid -> rid
						prid = pwid + merge_threshold
						
						#
						pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
						p.dag.add_node(pname, {'task':PutTask(pname, rid, prid, msgsize, block)})
						positions[pname] = (rid+0.1+idx/(factor-1), -sid+0.2)

						#
						p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), pname)
						p.dag.add_edge(pname, 'r'+str(prid)+'c'+str(sid))

			# 
			stage_mask *= factor
		
		elif stage.stype is StageType.invmerge:
			# decode
			merge_threshold = stage.arg1
			groups = stage.arg2
			factor = stage.arg3
			group_size = stage.arg3 * stage_mask

			for rid in range(size):
				if rid < merge_threshold:
					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
					positions[name] = (rid, -sid)

				else:
					wid = wids[rid]

					# normal factor exchange
					group = (wid // group_size) * group_size

					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.dag.add_node(name, {'task':ComputeTask(name, rid, delay=10)})
					p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), name)
					positions[name] = (rid, -sid)
					
					# for each group peer
					for idx in range(factor-1):
						# staggered multicast
						mask = (idx + 1) * stage_mask
						offset = (wid + mask) % group_size
						pwid = group + offset
						
						# convert wid -> rid
						prid = pwid + merge_threshold
						
						#
						pname = 'r' + str(rid) + 'p' + str(sid) + '_' + str(idx)
						p.dag.add_node(pname, {'task':PutTask(pname, rid, prid, msgsize, block)})
						positions[pname] = (rid+0.1+idx/(factor-1), -sid+0.2)

						#
						p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), pname)
						p.dag.add_edge(pname, 'r'+str(prid)+'c'+str(sid))

					# outmerge
					for idx in range(merge_threshold):
						if idx % groups == wid % groups:
							#
							pname = 'r' + str(rid) + 'p' + str(sid) + '_m' + str(idx)
							p.dag.add_node(pname, {'task':PutTask(pname, rid, idx, msgsize, block)})
							p.dag.add_edge('r'+str(rid)+'c'+str(sid-1), pname)
							p.dag.add_edge(pname, 'r'+str(idx)+'c'+str(sid))
							positions[pname] = (rid+0.1, -sid+0.1)

		else:
			raise ValueError('Unknown StageType.')

	# testing
	#nx.draw_networkx(p.dag, pos=positions)
	#plt.show()		

	return p

if __name__ == "__main__":
	size = 5
	schedule = [Stage(StageType.merge, 1, 2, 2), Stage(StageType.invmerge, 1, 2, 2)]
	block = False

	p = schedule_to_program_generator(size, schedule, block)
