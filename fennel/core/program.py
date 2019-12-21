"""
Defines the Program class.
"""


from typing import MutableMapping, Iterable


from fennel.core.task import Task
from fennel.tasks.start import StartTask


class Program:
    """
    A Program instance holds a DAG of Task instances which represents a
    executable program.
    """

    def __init__(self):
        self.edges_in: MutableMapping[str, str] = {}
        self.edges_out: MutableMapping[str, str] = {}
        self.metadata: MutableMapping[str, Task] = {}

    def get_task(self, name: str) -> Task:
        """
        Get a task by name.
        """

        return self.metadata[name]

    def add_node(self, name: str, task: Task) -> None:
        """
        Adds a node to this program.
        """

        self.metadata[name] = task

    def add_edge(self, name_from: str, name_to: str) -> None:
        """
        Adds an edge to this program.
        """

        # insert into out edges
        if name_from not in self.edges_out:
            self.edges_out[name_from] = [name_to]

        else:
            self.edges_out[name_from].append(name_to)

        # doubly link
        if name_to not in self.edges_in:
            self.edges_in[name_to] = [name_from]

        else:
            self.edges_in[name_to].append(name_from)

    def get_process_count(self) -> int:
        """
        Get number of processes required by program, the number of start tasks.
        """

        return len(self.get_start_tasks)

    def get_start_tasks(self) -> Iterable[StartTask]:
        """
        Get all start tasks in the program.
        """

        return {task for task in self.metadata.values()
                if isinstance(task, StartTask)}

    def get_successors_to_task(self, name):
        """
        Get all tasks that depend on this task.
        """

        # end of process check
        if name in self.edges_out:
            # dependent tasks
            for eid in self.edges_out[name]:
                yield eid

    def get_in_degree(self, nid):
        """
        """

        if nid in self.edges_in:
            return len(self.edges_in[nid])

        else:
            return 0

    def get_out_degree(self, nid):
        """
        """

        if nid in self.edges_out:
            return len(self.edges_out[nid])

        else:
            return 0

#    def convert_networkx(self):
#        import networkx as nx
#
#        graph = nx.Graph()
#
#        graph.add_nodes_from(self.metadata)
#
#        graph.add_edges_from([(out, d) for out, inl in self.edges_out.items() for d in inl])
#
#        return graph
