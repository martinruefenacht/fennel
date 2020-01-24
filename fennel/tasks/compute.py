"""
"""


from typing import Optional


from fennel.core.task import Task


class ComputeTask(Task):
    """
    ComputeTask represents the time of a model during which no communication
    takes place.
    """

    def __init__(self,
                 name: str,
                 node: int,
                 size: Optional[int] = None,
                 concurrent: bool = False):
        super().__init__(name, node, concurrent)

        self._size = size
        self._time = None

    @property
    def size(self) -> int:
        """
        Get compute size.
        """

        return self._size

    @property
    def time(self) -> Optional:
        """
        Get fixed compute time.
        """

        return self._time

    @time.setter
    def time(self, time: int) -> None:
        """
        Sets the time.
        """

        self._time = time
