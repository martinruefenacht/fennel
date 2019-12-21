"""
Defines the Program class.
"""


from typing import MutableMapping, Iterable


from fennel.core.tasks import Task, StartTask


class Program:
    """
    A Program instance holds a DAG of Task instances which represents a
    executable program.
    """

    def __init__(self):
        self.edges_in: MutableMapping[str, str] = {}
        self.edges_out: MutableMapping[str, str] = {}
        self.metadata: MutableMapping[str, Task] = {}

    def get_task(self, nid: str) -> Task:
        """
        """

        return self.metadata[nid]

    def add_node(self, nid: str, task: Task) -> None:
        """
        Adds a node to this program.
        """

        self.metadata[nid] = task

    def add_edge(self, nidfrom: str, nidto: str) -> None:
        """
        Adds an edge to this program.
        """

        # insert into out edges
        if nidfrom not in self.edges_out:
            self.edges_out[nidfrom] = [nidto]

        else:
            self.edges_out[nidfrom].append(nidto)

        # doubly link
        if nidto not in self.edges_in:
            self.edges_in[nidto] = [nidfrom]

        else:
            self.edges_in[nidto].append(nidfrom)

    def get_node_count(self) -> int:
        """
        """

        size = 0

        for nid, task in self.metadata.items():
            if task.__class__.__name__ == "StartTask":
                size += 1

        return size

    def get_start_tasks(self) -> Iterable[StartTask]:
        """
        """

        for nid, task in self.metadata.items():
            if task.__class__.__name__ == "StartTask":
                yield task

    def get_start_nodes(self):
        for nid, task in self.metadata.items():
            if task.__class__.__name__ == "StartTask":
                yield nid

    def get_successors_to_task(self, nid):
        # end of process check
        if nid in self.edges_out:
            # dependent tasks
            for eid in self.edges_out[nid]:
                yield eid

    def get_in_degree(self, nid):
        if nid in self.edges_in:
            return len(self.edges_in[nid])

        else:
            return 0

    def get_out_degree(self, nid):
        if nid in self.edges_out:
            return len(self.edges_out[nid])

        else:
            return 0

#    def prt(self):
#        print(self.edges_out)
#        print(self.metadata)
#        print(self.edges_in)

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
