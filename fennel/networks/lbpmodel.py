"""
Defines the latency-bandwidth-pipeline model.
"""


from typing import cast, Union


from fennel.core.time import Time
from fennel.core.network import NetworkModel, NetworkTime
from fennel.tasks.put import PutTask
from fennel.tasks.get import GetTask


class LBPModel(NetworkModel):
    """
    Implementation of the latency-bandwidth-pipeline model.
    """

    def __init__(self, latency: int, bandwidth: float, pipeline: int):
        super().__init__()

        self._latency = latency
        self._bandwidth = bandwidth
        self._pipeline = pipeline

    def evaluate(self,
                 time: Time,
                 task: Union[PutTask, GetTask]
                 ) -> NetworkTime:
        """
        Evaluate the latency-bandwidth network model.
        """

        if isinstance(task, PutTask):
            return self._evaluate_put(time, task)

        if isinstance(task, GetTask):
            return self._evaluate_get(time, task)

        raise RuntimeError(f"Task {task} not recognized.")

    def _evaluate_put(self, time: Time, task: PutTask) -> NetworkTime:
        """

        """

        local = self._pipeline
        remote = int(local +
                     self._latency +
                     self._bandwidth * task.message_size)

        return NetworkTime(cast(Time, time + local),
                           cast(Time, time + remote))

    def _evaluate_get(self, time: Time, task: GetTask) -> NetworkTime:
        """

        """
        
        raise NotImplementedError

        # local non-blocking, cannot use buffer that is gotten
        #   but we don't always want it blocking

        # remote, modify the taken buffer
        # local blocking, use the buffer
