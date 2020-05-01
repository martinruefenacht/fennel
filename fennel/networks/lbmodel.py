"""
Defines the latency-bandwidth model.
"""


import random
from typing import Sequence


from scipy.stats import betaprime


from fennel.core.network import NetworkModel, NetworkTime
from fennel.tasks.put import PutTask


class LBModel(NetworkModel):
    """
    Implementation of the latency-bandwidth model.
    """

    def __init__(self, latency: int, bandwidth: float):
        super().__init__()

        self._latency = latency
        self._bandwidth = bandwidth

    def evaluate(self, task: PutTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth network model.
        """

        time = self._latency + int(task.message_size * self._bandwidth)

        return NetworkTime(time, time)


class NoisyLBModel(LBModel):
    """
    Implementation of the latency-bandwidth model with a noisy
    channel. Adds random noise to the latency.
    """

    def __init__(self, latency: int, bandwidth: float, stdev: float):
        super().__init__(latency, bandwidth)

        self.noise: Sequence = betaprime.rvs(2.0, 3.0, stdev, size=100)

    @property
    def noise(self) -> Sequence:
        """Access the noise set."""

        return self._noise

    @noise.setter
    def noise(self, noise: Sequence) -> None:
        """Set the noise set."""

        self._noise = noise

    def evaluate(self, task: PutTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth model with noise.
        """

        time = self._latency + int(task.message_size * self._bandwidth)
        time += random.choice(self.noise)

        return NetworkTime(time, time)
