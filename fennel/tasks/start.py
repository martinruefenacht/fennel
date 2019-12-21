"""
"""

from fennel.core.task import Task


class StartTask(Task):
    """
    The StartTask is the initial hook for a process.
    """

    def __init__(self, name: str, proc: int, skew: int = 0):
        super().__init__(name, proc)

        # initial skew time, asymmetric arrival time
        self._skew = skew

    @property
    def skew(self) -> int:
        """
        Get initial skew.
        """

        return self._skew
