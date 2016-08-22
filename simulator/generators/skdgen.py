#! /usr/bin/python3

import sys, math

import simulator.core.stage as stage

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
