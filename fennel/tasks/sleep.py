"""
SleepTask definition.
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
            delay: Optional[int] = None,
            until: Optional[int] = None) -> None:
        super().__init__(name, proc)

        if delay is None and until is None:
            raise RuntimeError("SleepTask requires either delay or until")

        if delay is not None and delay <= 0:
            raise ValueError("SleepTask requires delay > 0")

        if until is not None and until <= 0:
            raise ValueError("SleepTask requires until > 0")

        self._delay = delay
        self._until = until

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
