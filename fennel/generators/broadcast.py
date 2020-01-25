"""
Generators for broadcast operations.
"""

import math
from typing import Any, Optional, Tuple, Iterable, Collection
from itertools import tee
import logging


from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.put import PutTask
from fennel.tasks.compute import ComputeTask


# TODO broadcast
#
#   tree broadcast, binomial, binary
#   ring
#   scatter + allgather

def _rotate(root: int, idx: int, processes: int) -> int:
    """
    Calculates the modulus process index.
    """

    return (idx - root) % processes


def generate_broacast_ring(processes: int, root: int, size: int) -> Program:
    """
    Generate a broadcast program using a ring topology.
    """

    assert processes > 0
    assert size >= 0
    assert 0 <= root < processes

    prog = Program()

    # start tasks
    for nidx in range(processes):
        pidx = _rotate(root, nidx, processes)

        prog.add_node(StartTask(f's_{pidx}', pidx))
        prog.add_node(ProxyTask(f'x_{pidx}', pidx))

    if processes == 1:
        prog.add_edge(f's_0', f'x_0')

        return prog

    prior = _rotate(root, processes-1, processes)
    fake = prior + 1

    prog.add_node(ProxyTask(f'p_{prior}_{fake}', prior))
    prog.add_edge(f's_{prior}', f'p_{prior}_{fake}')
    prog.add_edge(f'p_{prior}_{fake}', f'x_{prior}')

    for proc in range(processes - 2, -1, -1):
        source = _rotate(root, proc, processes)
        target = _rotate(root, proc + 1, processes)

        put_name = f'p_{source}_{target}'

        prog.add_node(PutTask(put_name, source, target, size))
        prog.add_edge(put_name, f'p_{target}_{target+1}')

        prog.add_edge(f's_{source}', put_name)
        prog.add_edge(put_name, f'x_{source}')

    return prog


def generate_broacast_binomial_tree(processes: int, message_size: int) -> Program:
    """
    """

    raise NotImplementedError

def generate_broacast_scatter_allgather(processes: int, message_size: int) -> Program:
    """
    """

    raise NotImplementedError
