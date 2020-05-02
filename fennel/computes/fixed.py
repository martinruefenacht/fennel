"""
Defines the fixed time compute model.
"""


from typing import cast


from fennel.core.time import Time, TimeSpan
from fennel.core.compute import ComputeModel
from fennel.tasks.compute import ComputeTask


class FixedTimeModel(ComputeModel):
    """
    The simplest compute model.
    """

    def __init__(self, duration: TimeSpan):
        super().__init__()

        self._duration = duration

    @property
    def duration(self) -> TimeSpan:
        """
        Gets duration.
        """

        return cast(TimeSpan, self._duration)

    def evaluate(self, time: Time, task: ComputeTask) -> Time:
        """
        Evaluate the fixed time model.
        """

        if task.time is not None:
            return cast(Time, time + task.time)

        # ignores the size of the task
        return cast(Time, time + self._duration)
