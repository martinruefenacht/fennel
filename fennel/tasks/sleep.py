"""
"""


from typing import Optional


from fennel.core.task import Task


class SleepTask(Task):
    """
    SleepTask specifies a time delay for this process.
    """

    def __init__(
            self,
            name: str,
            proc: int,
            delay: int = None,
            until: int = None):
        # initialize Task
        super().__init__(name, proc)

        self._delay: Optional[int] = delay
        self._until: Optional[int] = until

    @property
    def delay(self) -> Optional[int]:
        """
        Get the delay value.
        """

        return self._delay

    @property
    def until(self) -> Optional[int]:
        """
        Get the until value.
        """

        return self._until
