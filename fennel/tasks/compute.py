"""
"""

from fennel.core.task import Task


class ComputeTask(Task):
    """
    ComputeTask represents the time of a model during which no communication
    takes place.
    """

    def __init__(self, name: str, node: int, size: int, concurrent: bool):
        super().__init__(name, node, concurrent)

        self._size = size
        self._concurrent = False

    @property
    def size(self) -> int:
        """
        Get compute time.
        """

        return self._size

    @property
    def concurrent(self) -> bool:
        """
        Get threadablility of this compute task.
        """

        return self._concurrent
