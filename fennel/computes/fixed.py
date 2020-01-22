"""
Defines the fixed time compute model.
"""


from fennel.core.compute import ComputeModel
from fennel.tasks.compute import ComputeTask


class FixedTimeModel(ComputeModel):
    """
    The simplest compute model.
    """

    def __init__(self, duration: int):
        super().__init__()

        self._duration = duration

    @property
    def duration(self) -> int:
        """
        Gets duration.
        """

        return self._duration

    def evaluate(self, task: ComputeTask) -> int:
        """
        Evaluate the fixed time model.
        """

        # ignores the size of the task
        return self._duration
