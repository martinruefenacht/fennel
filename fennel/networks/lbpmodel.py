"""
Defines the latency-bandwidth-pipeline model.
"""


from typing import Tuple


from fennel.core.network import NetworkModel, NetworkTime
from fennel.tasks.put import PutTask


class LBPModel(NetworkModel):
    """
    Implementation of the latency-bandwidth-pipeline model.
    """

    def __init__(self, latency: int, bandwidth: float, pipeline: int):
        super().__init__()

        self._latency = latency
        self._bandwidth = bandwidth
        self._pipeline = pipeline

    def evaluate(self, time: int, task: PutTask) -> NetworkTime:
        """
        Evaluate the latency-bandwidth network model.
        """

        local = self._pipeline
        remote = int(local +
                     self._latency +
                     self._bandwidth * task.message_size)

        return NetworkTime(time + local, time + remote)
