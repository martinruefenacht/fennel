#! /usr/bin/python3

import sys, math

import simulator.core.stage as stage

import simulator.generators.skdgen as skdgen
import simulator.core.program as program
import simulator.core.tasks as tasks


from sympy import factorint
from itertools import combinations
from collections import Counter
from functools import reduce
import operator

def convert(primedict):
	schedule = []

	for factor, count in primedict.items():
		for c in range(count):
			schedule.append(stage.Stage(stage.StageType.factor, factor))
	
	return tuple(schedule)

def generate_factored(N):
	# find prime schedule
	prime_schedule = convert(factorint(N))

	# prime schedule -> combinations
	unique = []

	stack = []
	stack.append(prime_schedule)

	while stack:
		# retrieve item
		item = stack.pop()

		# check if done
		if item not in unique:
			# add to unique set
			unique.append(item)

			# check for combinations
			if len(item) is not 1:
				# create pairings
				pairs = set(combinations(item, 2))

				for pair in pairs:
					# subtract pair
					diff_set = Counter(item) - Counter(pair)

					# calculate product of pair
					value = stage.Stage(stage.StageType.factor, pair[0].arg1 * pair[1].arg1)

					# combine into new set
					combine_set = diff_set + Counter([value])
					
					# convert to stages
					combined = []
					for elem in combine_set.elements():
						combined.append(elem)

					# push to stack
					stack.append(tuple(combined))

	return unique

def generate_splits(N):
	schedules = []
	
	for threshold in range(2, N+1):
		for base in range(2, threshold+1):
			if threshold/base == threshold//base:
				s = generate_split(N, threshold, base)

				schedules.extend(s)

	return schedules
					
def generate_split(N, threshold, base):
	if (threshold // base) != (threshold / base):
		raise ValueError

	schedules = []

	# calculate number of remaining peers
	peers = threshold / base + (N - threshold)

	# factor peers
	subs = generate_factored(peers)

	for sub in subs:
		construct = []
		construct.append(stage.Stage(stage.StageType.split, threshold, base))
		construct.extend(sub)
		construct.append(stage.Stage(stage.StageType.invsplit, threshold, base))

		schedules.append(tuple(construct))
	
	return schedules

def generate_merge(N, r):
	if r < 1:
		return None

	peers = N - r
	subs = generate_factored(peers)

	schedules = []

	for sub in subs:
		# check that the sub schedule is suitable, ie > than 2
		if len(sub) < 2:
			continue

		# change first and last stages
		first = sub[0]
		last = sub[-1]

		# eval groups
		fgroups = reduce(operator.mul, (stage.arg1 for stage in sub[1:]))

		nfirst = stage.Stage(stage.StageType.merge, r, fgroups, first.arg1)

		lgroups = reduce(operator.mul, (stage.arg1 for stage in sub[:-1]))

		nlast = stage.Stage(stage.StageType.invmerge, r, lgroups, last.arg1)

		s = []
		s.append(nfirst)
		s.extend(sub[1:-1])
		s.append(nlast)
		
		schedules.append(tuple(s))
		
	return schedules

def generate_merges(N):
	schedules = []
	
	for r in range(1, N-3):
		s = generate_merge(N, r)
		
		if s is not None:
			schedules.extend(s)

	return schedules




def schedule_to_program_generator(scheduleob, block=False, block_size=1):
	msgsize = 8 
	p = program.Program()

	size = scheduleob.getProcessCount()
	schedule = scheduleob.order

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
