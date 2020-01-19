"""
Defines the latency-bandwidth model.
"""


from fennel.core.network import NetworkModel
from fennel.tasks.put import PutTask


class LBPModel(NetworkModel):
    """
    Implementation of the latency-bandwidth model.
    """

    def __init__(self, latency: int, bandwidth: float, pipeline: int):
        super().__init__()

        self._latency = latency
        self._bandwidth = bandwidth
        self._pipeline = pipeline

    def evaluate(self, task: PutTask) -> (int, int):
        """
        Evaluate the latency-bandwidth network model.
        """

        local = self._pipeline
        remote = local + self._latency + self._bandwidth * task.message_size

        return (local, remote)
