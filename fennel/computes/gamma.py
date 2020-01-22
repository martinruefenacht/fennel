"""
Defines the gamma compute model.
"""


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

    def evaluate(self, time: int, task: ComputeTask) -> int:
        """
        Evaluate the gamma model.
        """

        return time + int(task.size * self._gamma)


class ConcurrentGamma(ComputeModel):
    """
    Implements the GammaModel with multi-process allowing concurrent
    computation.

    TODO this really should be a ConcurrentMachine, not a concurrent task model
    """

    def __init__(self, gamma: float, concurrency: int):
        super().__init__()

        assert gamma >= 0.0
        assert concurrency >= 1

        self._gamma = gamma
        self._concurrency = concurrency

        self._concurrent_times = [0] * self._concurrency

    def evaluate(self, time: int, task: ComputeTask) -> int:
        """
        Evaluate the concurrent gamma model.
        """

        # operates on slots of concurrency
        # ----------------------------->
        # |-------|--------|------|
        # |----|--------|----|------|
        # |----------------|----|
        # |-------------------------|
        # ----------------------------->

        # find lowest thread time
        index = self._concurrent_times.index(min(self._concurrent_times))

        # evaluate gamma model
        compute_time = super().evaluate(self._concurrent_times[index], task)

        # set thread time and return dependency time
        self._concurrent_times[index] = compute_time

        return compute_time
