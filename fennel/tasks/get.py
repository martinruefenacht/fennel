"""
GetTask definition. One-sided fetch.
"""

from fennel.core.task import Task


class GetTask(Task):
    """
    Represents an RDMA get.
    """

    def __init__(self,
                 name: str,
                 proc: int,
                 target: int,
                 size_retrieve: int,
                 size_command: int = 8,
                 block: bool = True):
        super().__init__(name, proc)

        self._target = target
        self._size_retrieve = size_retrieve
        self._size_command = size_command
        self._block = block

    @property
    def target(self) -> int:
        """
        Get target of get operation.
        """

        return self._target

    @property
    def retrieval_message_size(self) -> int:
        """
        Get the retrival message size.
        """

        return self._size_retrieve

    @property
    def command_message_size(self) -> int:
        """
        Get the command message size.
        """

        return self._size_command

    @property
    def blocking(self) -> bool:
        """
        Get whether the operation is blocking.
        """

        return self._block
