"""
"""

from fennel.core.task import Task


class SleepTask(Task):
    """
    SleepTask specifies a time delay for this process.
    """

    def __init__(self, name: str, proc: int, delay: int):
        # initialize Task
        super().__init__(name, proc)

        # initialize SleepTask
        self._delay = delay

    @property
    def delay(self) -> int:
        """
        Get the delay value.
        """

        return self._delay
