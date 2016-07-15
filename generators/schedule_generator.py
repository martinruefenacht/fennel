#! /usr/bin/python3

import sys, math
from enum import Enum

from sympy import factorint
from itertools import combinations
from collections import Counter
from functools import reduce
import operator

class StageType(Enum):
	factor = 1
	split = 2
	invsplit = 3
	merge = 4
	invmerge = 5

class Stage:
	def __init__(self, stype, arg1, arg2=None, arg3=None):
		self.stype = stype
		self.arg1 = arg1
		self.arg2 = arg2
		self.arg3 = arg3
	
	def __str__(self):
		base = str(self.stype.name) + ':' + str(self.arg1)
		
		if self.arg2 is not None:
			base += ':' + str(self.arg2)

		if self.arg3 is not None:
			base += ':' + str(self.arg3)

		return base

	def __eq__(self, other):
		eq = (self.stype == other.stype) 
		eq = eq and (self.arg1 == other.arg1)
		eq = eq and (self.arg2 == other.arg2)
		eq = eq and (self.arg3 == other.arg3)
	
		return eq	

	def __hash__(self):
		xor = self.stype.value ^ self.arg1

		if self.arg2 is not None:
			xor ^= self.arg2

		if self.arg3 is not None:
			xor ^= self.arg3

		return xor
			

	def __repr__(self):
		return self.__str__()

def convert(primedict):
	schedule = []

	for factor, count in primedict.items():
		for c in range(count):
			schedule.append(Stage(StageType.factor, factor))
	
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
					value = Stage(StageType.factor, pair[0].arg1 * pair[1].arg1)

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
		construct.append(Stage(StageType.split, threshold, base))
		construct.extend(sub)
		construct.append(Stage(StageType.invsplit, threshold, base))

		schedules.append(tuple(construct))
	
	return schedules

def generate_merge(N, r):
	if r < 1:
		raise ValueError

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

		nfirst = Stage(StageType.merge, r, fgroups, first.arg1)

		lgroups = reduce(operator.mul, (stage.arg1 for stage in sub[:-1]))

		nlast = Stage(StageType.invmerge, r, lgroups, last.arg1)

		s = []
		s.append(nfirst)
		s.extend(sub[1:-1])
		s.append(nlast)
		
		schedules.append(tuple(s))
		
	return schedules

def generate_merges(N):
	schedules = []
	
	for r in range(1, N-4):
		s = generate_merge(N, r)
		
		if s is not None:
			schedules.extend(s)

	return schedules

if __name__ == '__main__':
	N = int(sys.argv[1])


	for s in generate_factored(N):
		print(s)
	print()

	for s in generate_splits(N):
		print(s)
	print()

	for s in generate_merges(N):
		print(s)
