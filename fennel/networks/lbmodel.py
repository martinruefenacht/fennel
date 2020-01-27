"""
Defines the latency-bandwidth model.
"""


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
