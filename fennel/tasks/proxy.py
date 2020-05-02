"""
ProxyTask definition.
"""

from fennel.core.task import Task


class ProxyTask(Task):
    """
    The ProxyTask is an empty task used be to able to not trigger
    another task.
    """

    def __repr__(self) -> str:
        return f'proxy {self._name}'
