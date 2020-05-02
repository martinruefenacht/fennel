"""
ComputeTask definition.
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
                 time: Optional[int] = None,
                 concurrent: bool = False):
        super().__init__(name, node, concurrent)

        if time is None and size is None:
            raise RuntimeError('ComputeTask needs either size or time.')

        if time and size:
            raise RuntimeError('ComputeTask needs either size or time.')

        if size is not None and size <= 0:
            raise ValueError('ComputeTask needs size > 0')

        if time is not None and time <= 0:
            raise ValueError('ComputeTask needs time > 0')

        self._size = size
        self._time = time

    def __repr__(self) -> str:
        if self._size:
            return f'compute {self._name} size {self._size}'

        return f'compute {self._name} time {self._time}'

    @property
    def size(self) -> Optional[int]:
        """
        Get compute size.
        """

        return self._size

    @size.setter
    def size(self, size: int) -> None:
        """
        Sets the size.
        """

        self._size = size

    @property
    def time(self) -> Optional[int]:
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
