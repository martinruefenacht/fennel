from scipy.stats import *
from random import choice

class NoiseGenerator:
	def generate(self, duration):
		raise NotImplementedError

class HistogramHoise(NoiseGenerator):
	def __init__(self, data):
		pass
	
	def generate(self, duration):
		raise NotImplementedError

class BetaPrimeNoise(NoiseGenerator):
	def __init__(self, a, b, scale=0.05):
		self.a = a
		self.b = b
		self.scale = scale
 
	def generate(self, duration):
		return int(round(betaprime.rvs(self.a, self.b, scale=duration*self.scale)))

class InvGaussNoise(NoiseGenerator):
	def __init__(self, mu, loc, scale):
		self.mu = mu
		self.loc = loc
		self.scale = scale

	def generate(self, duration):
		return int(round(invgauss.rvs(self.mu, self.loc, self.scale)))

class GammaNoise(NoiseGenerator):
	def __init__(self, alpha, loc, scale):
		self.alpha = alpha
		self.loc = loc
		self.scale = scale

	def generate(self, duration):
		return int(round(gamma.rvs(self.alpha, self.loc, self.scale)))
