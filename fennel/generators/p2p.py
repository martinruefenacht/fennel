"""
Module for generators of point-to-point programs.
"""

from fennel.core.program import Program
from fennel.core.tasks import StartTask, PutTask, ProxyTask


def generate_multicast(message_size: int, width: int) -> Program:
    """
    Generate a multicast program.
    """

    assert message_size >= 0
    assert width >= 1

    prog = Program()

    nodes = width + 1

    # create start nodes
    for cidx in range(nodes):
        prog.add_node(f's_{cidx}', StartTask(f's_{cidx}', cidx))

    # create put nodes
    for cidx in range(1, nodes):
        prog.add_node(f'p0_{cidx}',
                      PutTask(f'p0_{cidx}', 0, cidx, message_size))
        prog.add_edge(f's_{cidx}', f'p0_{cidx}')
        prog.add_edge('s_0', f'p0_{cidx}')

    return prog


def generate_pingpong(message_size: int, rounds: int) -> Program:
    """
    Generate a ping pong program.
    """

    assert message_size >= 0
    assert rounds > 0

    prog = Program()

    prog.add_node('s0', StartTask('s0', 0))
    prog.add_node('s1', StartTask('s1', 1))

    prog.add_node('x0_0', ProxyTask('x0_0', 0))
    prog.add_node('x1_0', ProxyTask('x1_0', 1))

    prog.add_edge('s0', 'x0_0')
    prog.add_edge('s1', 'x1_0')

    for ridx in range(0, rounds):
        prog.add_node(f'p0_{ridx}', PutTask(f'p0_{ridx}', 0, 1, message_size))
        prog.add_node(f'p1_{ridx}', PutTask(f'p1_{ridx}', 1, 0, message_size))

        prog.add_edge(f'x0_{ridx}', f'p0_{ridx}')
        prog.add_edge(f'x1_{ridx}', f'p1_{ridx}')

        prog.add_node(f'x0_{ridx+1}', ProxyTask(f'x0_{ridx+1}', 0))
        prog.add_node(f'x1_{ridx+1}', ProxyTask(f'x1_{ridx+1}', 1))

        prog.add_edge(f'p0_{ridx}', f'x0_{ridx+1}')
        prog.add_edge(f'p1_{ridx}', f'x1_{ridx+1}')

        # ping
        prog.add_edge(f'p0_{ridx}', f'p1_{ridx}')

        # pong
        prog.add_edge(f'p1_{ridx}', f'x0_{ridx+1}')

    return prog
