"""
Defines the gamma compute model.
"""


import random
import math
from typing import Sequence, cast


from scipy.stats import betaprime  # type: ignore


from fennel.core.time import Time
from fennel.core.compute import ComputeModel
from fennel.tasks.compute import ComputeTask


class GammaModel(ComputeModel):
    """
    The simplest compute model.
    """

    def __init__(self, gamma: float):
        super().__init__()

        if gamma < 0.0:
            raise RuntimeError("Gamma is not allowed to be negative.")

        self._gamma = gamma

    @property
    def gamma(self) -> float:
        """
        Gets gamma.
        """

        return self._gamma

    def _evaluate_independent(self, task: ComputeTask) -> int:
        """
        Evaluates the task independent of when.
        """

        if task.time is not None:
            return task.time

        assert task.size is not None
        return int(task.size * self._gamma)

    def evaluate(self, time: Time, task: ComputeTask) -> Time:
        """
        Evaluate the gamma model.
        """

        return cast(Time, time + self._evaluate_independent(task))


class NoisyGammaModel(GammaModel):
    """
    A noise influenced GammaModel.

    The noise distribution is a Betaprime distribution(2,3).
    The noise function sample is then used as a percentage + 100%.
    """

    def __init__(self, gamma: float, stdev: float):
        super().__init__(gamma)

        self._noise: Sequence = betaprime.rvs(2.0, 3.0, stdev, size=100)

    @property
    def noise(self) -> Sequence:
        """Access the noise set."""

        return self._noise

    def _evaluate_independent(self, task: ComputeTask) -> int:
        """
        Evaluates the task independent of when.
        """

        noise = random.choice(self._noise)

        if task.time is not None:
            return task.time + noise

        assert task.size is not None
        return int(task.size * self._gamma * (1.0 + noise))


# class SinusoidalGammaModel(GammaModel):
#     """
#     """
#
#     def __init__(self,
#                  gamma: float,
#                  freq: float,
#                  amplitude: float,
#                  offset: float = 0.0):
#         """
#         """
#
#         assert 1.0 > amplitude >= 0.0
#
#         self._gamma = gamma
#         self._freq = freq
#         self._amplitude = amplitude
#         self._offset = offset
#
#     def evaluate(self, time: int, task: ComputeTask) -> Time:
#         """
#         """
#
#         if task.time is not None:
#             return cast(Time, time + task.time)
#
#         assert task.size is not None
#         return cast(Time,
#             time + int(task.size * self._gamma * (
#             1.0 + self._amplitude * math.sin(
#                 time * self._freq + self._offset))))
