"""
Generators for a BSP style model.
"""


from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.start import StartTask


import random


def single_superstep(
        nodes: int,
        msgsize: int,
        rounds: int = 1
        ):
    """
    Generates a program with a single compute step.
    """

    random.seed(12345)

    prog = Program()

    prog.add_node(ProxyTask("b_0", 0))

    # generate start tasks
    for nidx in range(nodes):
        prog.add_node(StartTask(f"s_{nidx}",
                                nidx,
                                skew=random.randint(0, 100)))

        prog.add_edge(f"s_{nidx}", "b_0")

    # barrier are not node specific, why are proxies??
    # Task fundamentally requires a node
    # is placing a nidx=0 okay? It would be cleaner if we didnt need to do that

    for ridx in range(1, rounds + 1):
        prog.add_node(ProxyTask(f"b_{ridx}", 0))

        for nidx in range(nodes):
            prog.add_node(ComputeTask(f"c_{nidx}_{ridx}",
                                      nidx,
                                      random.randint(10, msgsize)))

            prog.add_edge(f"b_{ridx-1}", f"c_{nidx}_{ridx}")
            prog.add_edge(f"c_{nidx}_{ridx}", f"b_{ridx}")

    # finishing proxies
    for nidx in range(nodes):
        prog.add_node(ProxyTask(f"x_{nidx}", nidx))
        prog.add_edge(f"b_{rounds}", f"x_{nidx}")

    return prog
