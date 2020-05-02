"""
The PutTask is defined, one-sided send.
"""

from fennel.core.task import Task


class PutTask(Task):
    """
    Represents an RDMA put.
    """

    def __init__(self,
                 name: str,
                 proc: int,
                 target: int,
                 size: int,
                 block: bool = True):
        super().__init__(name, proc)

        self._target = target
        self._size = size
        self._block = block

    @property
    def target(self) -> int:
        """
        Get target of put operation.
        """

        return self._target

    @property
    def message_size(self) -> int:
        """
        get put message size.
        """

        return self._size

    @property
    def size(self) -> int:
        """
        get put message size.
        """

        return self.message_size

    @property
    def blocking(self) -> bool:
        """
        Get whether the operation is blocking.
        """

        return self._block
