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


def generate_broacast_ring(processes: int, root: int, size: int) -> Program:
    """
    Generate a broadcast program using a ring topology.
    """

    assert processes > 0
    assert size >= 0
    # assert 0 <= root < processes

    prog = Program()

    # start tasks
    for nidx in range(processes):
        prog.add_node(StartTask(f's_{nidx}', nidx))
        prog.add_node(ProxyTask(f'x_{nidx}', nidx))

    if processes == 1:
        prog.add_edge(f's_{nidx}', f'x_{nidx}')
        return prog

    prog.add_node(ProxyTask(f'p_{processes-1}_{processes}', processes-1))
    prog.add_edge(f's_{processes-1}', f'p_{processes-1}_{processes}')
    prog.add_edge(f'p_{processes-1}_{processes}', f'x_{processes-1}')

    for proc in range(processes - 2, -1, -1):
        target = proc + 1
        source = proc

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
