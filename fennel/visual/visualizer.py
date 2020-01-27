"""
"""


# pylint: disable=protected-access


from typing import Mapping


from pyvis.network import Network


from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask

from fennel.generators.p2p import generate_send_partitioned_p2p
from fennel.generators.compute import generate_compute
from fennel.generators.broadcast import generate_broacast_ring
from fennel.generators.p2p import generate_multicast
from fennel.generators.p2p import generate_send
from fennel.generators.allreduce import generate_recursive_doubling


def _find_maximum(name: str, program: Program, level: int = 0) -> int:
    """
    Calculate path to starttask.
    """

    if isinstance(program._metadata[name], StartTask):
        return level

    parent_levels = []
    for parent in program._edges_in[name]:
        parent_levels.append(_find_maximum(parent, program, level+1))

    return max(parent_levels)


def _calculate_levels(program: Program) -> Mapping:
    """
    """

    levels = {}

    for name, task in program._metadata.items():
        levels[name] = _find_maximum(name, program)

    return levels


def convert(program: Program) -> Network:
    """
    Convert a program into a pyvis Network.
    """

    net = Network(height='100%', width='100%',
                  directed=True, layout=True)
    net.hrepulsion(spring_strength=0.1)

    # determine levels for all task
    levels = _calculate_levels(program)

    # add all tasks as nodes
    for name, task in program._metadata.items():
        net.add_node(name,
                     level=levels[name],
                     label=task.__class__.__name__,
                     x=task.node)
#                     group=task.__class__.__name__)

    # add all edges required
    for name in program._metadata.keys():
        names = program.get_predecessors(name)
        for sub in names:
            color = '#05668D'

            if program[name].any is not None:
                color = '#679436'

            net.add_edge(sub, name, color=color)

    return net


def main() -> None:
    """
    Main function.
    """

    # prog = generate_multicast(1, 5, False)
    # prog = generate_send(0, False)
    # prog = generate_compute(1, 4, 10, concurrent=False, rounds=5)
    # prog = generate_recursive_doubling(16, 0)

    prog = generate_send_partitioned_p2p(1024 * 16,
                                         4,
                                         3,
                                         2)

    net = convert(prog)

    net.show('test.html')


if __name__ == "__main__":
    main()
