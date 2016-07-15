from enum import Enum

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

