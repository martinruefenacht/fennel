from abc import ABCMeta, abstractmethod
from scipy.stats import betaprime
from random import choice

class NoiseGenerator:
	@abstractmethod
	def generate(self):
		pass

class BetaPrimeNoise(NoiseGenerator):
	def __init__(self, a, b, loc=0, scale=20):
		self.lookup = [int(round(i)) for i in betaprime.rvs(a, b, loc=loc, scale=scale, size=1000)]
 
	def generate(self):
		return choice(self.lookup)
