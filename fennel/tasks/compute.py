"""
"""

from fennel.core.task import Task


class ComputeTask(Task):
    """
    ComputeTask represents the time of a model during which no communication
    takes place.
    """
    def __init__(self, name: str, proc: int, size: int):
        # initialize task
        super().__init__(name, proc)

        # initialize compute task
        self._size = size

    @property
    def size(self) -> int:
        """
        Get compute time.
        """

        return self._size
