from abc import ABCMeta, abstractmethod
from scipy.stats import betaprime
from random import choice

class NoiseGenerator:
	def generate(self, duration):
		raise NotImplementedError

class BetaPrimeNoise(NoiseGenerator):
	def __init__(self, a, b, scale=0.05):
		self.a = a
		self.b = b
		self.scale = scale
 
	def generate(self, duration):
		return int(round(betaprime.rvs(self.a, self.b, scale=duration*self.scale)))
