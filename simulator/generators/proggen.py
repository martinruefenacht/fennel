#! /usr/bin/python3

import simulator.core.stage as stage
import simulator.generators.skdgen as skdgen
import simulator.core.program as program
import simulator.core.tasks as tasks

def schedule_to_program_generator(size, schedule, block):
	msgsize = 8 
	p = program.Program()

	# create start tasks
	for rid in range(size):
		name = 'r' + str(rid) + 'c0'
		p.addNode(name, tasks.StartTask(name, rid))

	# run through schedule
	split_stack = []
	stage_mask = 1
	wids = {}
	
	for scount, staget in enumerate(schedule):
		# stage id
		sid = scount + 1

		# if factor
		if staget.stype is stage.StageType.factor:
			# decode stage
			factor = staget.arg1

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
				p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
				
				# compute is dependent on previous compute
				p.addEdge('r' + str(rid) + 'c' + str(sid-1), name)

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
					ptask = tasks.PutTask(pname, rid, prid, msgsize, block)
					p.addNode(pname, ptask)
					
					# depends on previous compute
					p.addEdge('r' + str(rid) + 'c' + str(sid-1), pname)
					# add dependency for all follow computes
					p.addEdge(pname, 'r' + str(prid) + 'c' + str(sid)) 

			# increment mask
			stage_mask *= factor

		elif staget.stype is stage.StageType.split:
			# decode stage
			threshold = staget.arg1
			base = staget.arg2

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
						p.addNode(name, tasks.PutTask(name, rid, group_leader, msgsize, block))
						p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
	
					# if leader of group
					else:
						# assign working id
						wid = rid // group_size

						# construct compute
						name = 'r'+str(rid)+'c'+str(sid)
						p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
						p.addEdge('r'+str(rid)+'c'+str(sid-1), name)

						# add dependencies
						for idx in range(group_uppermost):
							pid = (rid // group_size) * group_size + idx
							pname = 'r' + str(pid) + 'p' + str(sid)
							p.addEdge(pname, name)							

				# above collapse region
				else:
					# assign wid
					wid = rid - int(groups * group_uppermost)

					# create proxy
					name = 'r' + str(rid) + 'c' + str(sid)
					p.addNode(name, tasks.ProxyTask(name, rid))
					p.addEdge('r' + str(rid) + 'c' + str(sid-1), name)

				# insert rid & wid into translation dict
				wids[rid] = wid

		elif stage.stype is stage.StageType.invsplit:
			# decode stage
			threshold = staget.arg1
			base = staget.arg2

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
							p.addNode(name, tasks.PutTask(name, rid, prid, msgsize, block))
							p.addEdge('r'+str(rid)+'c'+str(sid-1), name)

							p.addEdge(name, 'r'+str(prid)+'c'+str(sid))

					# if not leader
					else:
						# construct compute
						name = 'r' + str(rid) + 'c' + str(sid)
						p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
		
		elif staget.stype is stage.StageType.merge:
			# decode
			merge_threshold = staget.arg1
			groups = staget.arg2

			factor = staget.arg3
			group_size = staget.arg3 * stage_mask

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
						p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))
						p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
						p.addEdge(pname, 'r' + str(prid) + 'c' + str(sid))

				else:
					wid = rid - merge_threshold
					wids[rid] = wid
					
					# normal factor exchange
					group = (wid // group_size) * group_size

					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
					p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
					
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
						p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))
						positions[pname] = (rid+0.1+idx/(factor-1), -sid+0.2)

						#
						p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
						p.addEdge(pname, 'r'+str(prid)+'c'+str(sid))

			# 
			stage_mask *= factor
		
		elif staget.stype is stage.StageType.invmerge:
			# decode
			merge_threshold = staget.arg1
			groups = staget.arg2
			factor = staget.arg3
			group_size = staget.arg3 * stage_mask

			for rid in range(size):
				if rid < merge_threshold:
					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.addNode(name, tasks.ComputeTask(name, rid, delay=10))

				else:
					wid = wids[rid]

					# normal factor exchange
					group = (wid // group_size) * group_size

					# compute
					name = 'r' + str(rid) + 'c' + str(sid)
					p.addNode(name, tasks.ComputeTask(name, rid, delay=10))
					p.addEdge('r'+str(rid)+'c'+str(sid-1), name)
					
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
						p.addNode(pname, tasks.PutTask(pname, rid, prid, msgsize, block))

						#
						p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
						p.addEdge(pname, 'r'+str(prid)+'c'+str(sid))

					# outmerge
					for idx in range(merge_threshold):
						if idx % groups == wid % groups:
							#
							pname = 'r' + str(rid) + 'p' + str(sid) + '_m' + str(idx)
							p.addNode(pname, tasks.PutTask(pname, rid, idx, msgsize, block))
							p.addEdge('r'+str(rid)+'c'+str(sid-1), pname)
							p.addEdge(pname, 'r'+str(idx)+'c'+str(sid))

		else:
			raise ValueError('Unknown StageType.')

	return p
