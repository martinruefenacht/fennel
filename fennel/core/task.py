"""
"""

class Task:
    """
    """

    task_counter: int = 0

    def __init__(self, name: str, proc: int):
        self._name = name
        self._proc = proc

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
    def process(self) -> int:
        """
        Get process id
        """

        return self._proc

    @property
    def name(self) -> str:
        """
        Get process name.
        """

        return self._name
