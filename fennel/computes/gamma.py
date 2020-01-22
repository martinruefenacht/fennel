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
