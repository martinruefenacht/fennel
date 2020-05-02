"""
StartTask definition.
"""

from fennel.core.task import Task


class StartTask(Task):
    """
    The StartTask is the initial hook for a process.
    """

    def __init__(self, name: str, proc: int, skew: int = 0):
        super().__init__(name, proc)

        # initial skew time, asymmetric arrival time
        assert skew >= 0
        self._skew = skew

    def __repr__(self) -> str:
        if self._skew > 0:
            return f'start {self._name} skew {self._skew}'

        return f'start {self._name}'

    @property
    def skew(self) -> int:
        """
        Get initial skew.
        """

        return self._skew
