"""
Defines the gamma compute model.
"""


from fennel.core.compute import ComputeModel
from fennel.tasks.compute import ComputeTask

from scipy.stats import norm
import random


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

    def evaluate(self, time: int, task: ComputeTask) -> int:
        """
        Evaluate the gamma model.
        """

        if task.time is not None:
            return time + task.time

        return time + int(task.size * self._gamma)


class NoisyGammaModel(GammaModel):
    """
    """

    def __init__(self, gamma: float, stdev: float):
        super().__init__(gamma)

        self._prep = norm.rvs(1.0, stdev, size=1000)

    def evaluate(self, time: int, task: ComputeTask) -> int:
        """
        Evaluate the gamma model.
        """

        if task.time is not None:
            return time + task.time

        noise = random.choice(self._prep)

        return time + int(task.size * self._gamma * noise)
