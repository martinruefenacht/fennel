"""
Defines the Program class.
"""


from typing import MutableMapping, Iterable, Optional, MutableSet, List, AbstractSet
from collections import defaultdict


from fennel.core.task import Task
from fennel.tasks.start import StartTask


class Program:
    """
    A Program instance holds a DAG of Task instances which represents a
    executable program.
    """

    def __init__(self):
        self._edges_in: MutableMapping[str, MutableSet[str]]
        self._edges_in = defaultdict(set)

        self._edges_out: MutableMapping[str, MutableSet[str]]
        self._edges_out = defaultdict(set)

        self._metadata: MutableMapping[str, Task] = dict()

    def get_task(self, name: str) -> Optional[Task]:
        """
        Get a task by name.
        """

        return self._metadata.get(name)

    def __getitem__(self, key: str) -> Optional[Task]:
        return self.get_task(key)

    def add_node(self, task: Task) -> None:
        """
        Adds a node to this program.
        """

        self._metadata[task.name] = task

    def add_edge(self, name_from: str, name_to: str) -> None:
        """
        Adds an edge to this program.
        """

        if name_from not in self._metadata:
            raise RuntimeError(f'{name_from} not in nodes.')

        if name_to not in self._metadata:
            raise RuntimeError(f'{name_to} not in nodes.')

        self._edges_out[name_from].add(name_to)
        self._edges_in[name_to].add(name_from)

    def get_process_count(self) -> int:
        """
        Get number of processes required by program, the number of start tasks.
        """

        return sum(isinstance(task, StartTask)
                   for task in self._metadata.values())

    def get_start_tasks(self) -> Iterable[StartTask]:
        """
        Get all start tasks in the program.
        """

        return (task for task in self._metadata.values()
                if isinstance(task, StartTask))

    def get_successors(self, name: str) -> AbstractSet[str]:
        """
        Get all tasks dependent on this task.
        """

        if name not in self._edges_out:
            return set()

        return self._edges_out[name]

    def get_predecessors(self, name: str) -> AbstractSet[str]:
        """
        Get all tasks who are predecessors.
        """

        if name not in self._edges_in:
            return set()

        return self._edges_in[name]

    def get_in_degree(self, name: str) -> int:
        """
        Get the number of dependencies of the node.
        """

        return len(self._edges_in[name])

    def get_out_degree(self, name: str) -> int:
        """
        Get the number of successors of the node.
        """

        return len(self._edges_out[name])
