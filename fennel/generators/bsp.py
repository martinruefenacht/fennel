"""
Generators for a BSP style model.
"""


from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.put import PutTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.start import StartTask


def single_superstep(
        nodes: int,
        msgsize: int
        ):
    """
    Generates a program with a single compute step.
    """

    prog = Program()

    prog.add_node(ProxyTask("b1", 0))
    prog.add_node(ProxyTask("b2", 0))

    # generate start tasks
    for nidx in range(nodes):
        prog.add_node(StartTask(f"s_{nidx}", nidx))

        prog.add_edge(f"s_{nidx}", "b1")

    # barrier are not node specific, why are proxies??
    # Task fundamentally requires a node
    # is placing a nidx=0 okay? It would be cleaner if we didnt need to do that

    # generate compute tasks
    for nidx in range(nodes):
        prog.add_node(ComputeTask(f"c_{nidx}", nidx, msgsize))
        prog.add_node(ProxyTask(f"x_{nidx}", nidx))

        prog.add_edge("b1", f"c_{nidx}")
        prog.add_edge(f"c_{nidx}", "b2")

        prog.add_edge("b2", f"x_{nidx}")
        prog.add_edge(f"c_{nidx}", f"x_{nidx}")

    return prog
