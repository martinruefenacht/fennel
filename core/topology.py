# procs will be numbered from [0, inf)
# distance between mapped is important

# TODO set proc location
# jobs are not usually allowed to be fixed size perfectly fitting topology

# proc #0 -> physical location #5
# proc #1 -> physical location #6 expected, but #10


##class Topology:
#	def minimum(proc1, proc2):
#		# give number of hops
#		raise NotImplementedError
#
#class AllToAll(Topology):
#	def minimum(proc1, proc2):
#		return 1
#
#class Star(Topology):
#	def __init__(self, center):
#		self.center = center
#	
#	def minimum(proc1, proc2):
#		if proc1 == self.center or proc2 == self.center:
#			return 1
#		else:
#			return 2
#
#class Ring(Topology):
#	def __init__(self, size):
#		self.size = size
#
#	def minimum(p1, p2):
#		path1 = p2 - p1
#		path2 = p2 - p1 - self.size
#
#		return path1 if path1 < path2 else path2
#
#class FatTree(Topology):
#	pass
#
#class DragonFly(Topology):
#	pass




