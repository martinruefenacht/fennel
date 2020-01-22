"""
"""

class Task:
    """
    """

    task_counter: int = 0

    def __init__(self, name: str, node: int, concurrent: bool = False):
        self._name = name
        self._node = node
        self._concurrent = concurrent

        self._taskid = Task.task_counter
        Task.task_counter += 1

    def __lt__(self, task):
        return self._taskid < task.taskid

    @property
    def taskid(self) -> int:
        """
        Get task id.
        """

        return self._taskid

    @property
    def node(self) -> int:
        """
        Get node id
        """

        return self._node

    @property
    def name(self) -> str:
        """
        Get task name.
        """

        return self._name

    @property
    def concurrent(self) -> bool:
        """
        Gets concurrency.
        """

        return self._concurrent
