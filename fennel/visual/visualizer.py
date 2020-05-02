"""
"""


# pylint: disable=protected-access


from typing import Mapping


from pyvis.network import Network  # type: ignore


from fennel.core.program import Program
from fennel.tasks.start import StartTask


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

            assert program[name] is not None
            if program[name].any is not None:
                color = '#679436'

            net.add_edge(sub, name, color=color)

    return net
