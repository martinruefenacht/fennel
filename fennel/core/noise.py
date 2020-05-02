"""
Abstraction of the noise generation.
"""

# from abc import ABC, abstractmethod
# from random import choice


# import scipy.stats


# class NoiseModel(ABC):
#     """
#     """

#     def __init__(self, seed: int) -> None:
#         self._seed = seed

#     @abstractmethod
#     def sample(self) -> int:
#         """
#         Sample the noise model.
#         """


# class NoNoiseModel(NoiseModel):
#     """
#     """

#     def __init__(self):
#         pass

#     def sample(self) -> int:
#         """
#         """

#         return 0


# class NormalNoise(NoiseModel):
#     """
#     """

#     def __init__(self, seed: int, mean: float, stdev: float) -> None:
#         super().__init__(seed)

#         self._mean = mean
#         self._stdev = stdev

#         rvs = scipy.stats.norm.rvs(self._mean, self._stdev,
#                                    size=100, random_state=self._seed)

#         self._rvs = [int(r) for r in rvs]

#     def sample(self) -> int:
#         """
#         Sample the normal distributed noise function.
#         """

#         return choice(self._rvs)
