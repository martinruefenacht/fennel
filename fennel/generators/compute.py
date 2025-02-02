"""
Module for generators of point-to-point programs.
"""


from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.compute import ComputeTask


def simple_compute(size: int, rounds: int = 1, node: int = 0) -> Program:
    """
    Generate a single process with compute tasks.
    """

    prog = Program()

    prog.add_node(StartTask('s', node))
    prog.add_node(ProxyTask('x_0', node))
    prog.add_edge('s', 'x_0')

    for ridx in range(1, rounds + 1):
        prog.add_node(ProxyTask(f'x_{ridx}', node))
        prog.add_node(ComputeTask(f'c_{ridx}', node, size))

        prog.add_edge(f'x_{ridx-1}', f'c_{ridx}')
        prog.add_edge(f'c_{ridx}', f'x_{ridx}')

    return prog


def parallel_compute(nodes: int,
                     count: int,
                     size: int,
                     concurrent: bool,
                     rounds: int = 1) -> Program:
    """
    Generate a multicast program.
    """

    assert nodes >= 1
    assert count >= 1
    assert size >= 0
    assert rounds >= 1

    prog = Program()

    prog.add_node(StartTask('s', 0))
    prog.add_node(ProxyTask('x_0_1', 0))
    prog.add_edge('s', 'x_0_1')

    # handle iterable size, each round vs each process
    # if isinstance(size, Iterable):

    for block in range(1, rounds+1):
        prog.add_node(ProxyTask(f'x_{block}_0', 0))
        prog.add_edge(f'x_{block-1}_1', f'x_{block}_0')

        prog.add_node(ProxyTask(f'x_{block}_1', 0))

        for com in range(count):
            name = f'c_{block}_{com}'
            prog.add_node(ComputeTask(name,
                                      0,
                                      size,
                                      concurrent))

            prog.add_edge(f'x_{block}_0', name)
            prog.add_edge(name, f'x_{block}_1')

    return prog
