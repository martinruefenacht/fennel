"""
Simple common generators.
"""


from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.start import StartTask
from fennel.tasks.sleep import SleepTask


def sleep_until(
        nodes: int,
        time: int
        ):
    """
    Generates a program which sleeps until a global time.
    """

    prog = Program()

    for nidx in range(nodes):
        prog.add_node(StartTask(f"s_{nidx}", nidx))
        prog.add_node(SleepTask(f"t_{nidx}", nidx, until=time))
        prog.add_node(ProxyTask(f"x_{nidx}", nidx))

        prog.add_edge(f"s_{nidx}", f"t_{nidx}")
        prog.add_edge(f"t_{nidx}", f"x_{nidx}")

    return prog
