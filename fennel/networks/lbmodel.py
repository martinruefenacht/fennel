"""
Defines the latency-bandwidth model.
"""


import random
from typing import Sequence, cast, Union


from scipy.stats import betaprime  # type: ignore


from fennel.core.time import Time
from fennel.core.network import NetworkModel, NetworkTime
from fennel.tasks.put import PutTask
from fennel.tasks.get import GetTask


class LBModel(NetworkModel):
    """
    Implementation of the latency-bandwidth model.
    """

    def __init__(self, latency: int, bandwidth: float):
        super().__init__()

        self._latency = latency
        self._bandwidth = bandwidth

    def evaluate(self,
                 time: Time,
                 task: Union[PutTask, GetTask]
                 ) -> NetworkTime:
        """
        Evaluate task with appropriate handler.
        """

        if isinstance(task, PutTask):
            return self._evaluate_put(time, task)

        if isinstance(task, GetTask):
            return self._evaluate_get(time, task)

        raise RuntimeError(f"Task {task} not recognized.")

    def _evaluate_put(self, time: Time, task: PutTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth network model with a PutTask.
        """

        time_next = self._latency + int(task.message_size * self._bandwidth)
        time_next += time

        return NetworkTime(cast(Time, time_next), cast(Time, time_next))

    def _evaluate_get(self, time: Time, task: GetTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth network model with a GetTask.
        """

        time_remote = (time + self._latency +
                       int(task.command_message_size * self._bandwidth))
        time_local = (time_remote + self._latency +
                      int(task.retrieval_message_size * self._bandwidth))

        return NetworkTime(cast(Time, time_local), cast(Time, time_remote))


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

    def evaluate(self, time: int, task: PutTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth model with noise.
        """

        time_next = self._latency + int(task.message_size * self._bandwidth)
        time_next += random.choice(self.noise)
        time_next += time

        return NetworkTime(cast(Time, time_next), cast(Time, time_next))
