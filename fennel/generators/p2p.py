"""
Module for generators of point-to-point programs.
"""

from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.put import PutTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.compute import ComputeTask


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
        prog.add_node(StartTask(f's_{cidx}', cidx))

    # create put nodes
    for cidx in range(1, nodes):
        prog.add_node(PutTask(f'p0_{cidx}', 0, cidx, message_size))
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

    prog.add_node(StartTask('s0', 0))
    prog.add_node(StartTask('s1', 1))

    prog.add_node(ProxyTask('x0_0', 0))
    prog.add_node(ProxyTask('x1_0', 1))

    prog.add_edge('s0', 'x0_0')
    prog.add_edge('s1', 'x1_0')

    for ridx in range(0, rounds):
        prog.add_node(PutTask(f'p0_{ridx}', 0, 1, message_size))
        prog.add_node(PutTask(f'p1_{ridx}', 1, 0, message_size))

        prog.add_edge(f'x0_{ridx}', f'p0_{ridx}')
        prog.add_edge(f'x1_{ridx}', f'p1_{ridx}')

        prog.add_node(ProxyTask(f'x0_{ridx+1}', 0))
        prog.add_node(ProxyTask(f'x1_{ridx+1}', 1))

        prog.add_edge(f'p0_{ridx}', f'x0_{ridx+1}')
        prog.add_edge(f'p1_{ridx}', f'x1_{ridx+1}')

        # ping
        prog.add_edge(f'p0_{ridx}', f'p1_{ridx}')

        # pong
        prog.add_edge(f'p1_{ridx}', f'x0_{ridx+1}')

    return prog


def generate_partitioned_send(message_size: int,
                              partitions: int,
                              threshold: int,
                              rounds: int
                              ) -> Program:
    """
    Generate a two phase partitioned send Program.
    """

    # TODO this should be generalized
    # threshold value

    assert message_size >= 0
    assert partitions > 0
    assert threshold > 0 and threshold <= partitions
    assert rounds > 0

    program = Program()

    program.add_node(StartTask("s_0", 0))

    program.add_node(ProxyTask("x_0_0", 0))

    program.add_node(ComputeTask("c_0_0", 0, 1024))
    program.add_node(ComputeTask("c_0_1", 0, 1024))

    program.add_node(PutTask("p_0", 0, 1, 2048))

    program.add_node(ProxyTask("x_0_1", 0))

    program.add_node(ComputeTask("c_0_2", 0, 1024))
    program.add_node(ComputeTask("c_0_3", 0, 1024))

    program.add_node(PutTask("p_1", 0, 1, 2048))

    program.add_node(StartTask("s_1", 1))

    program.add_node(ProxyTask("x_1_0", 1))

    program.add_node(ComputeTask("c_1_0", 1, 1024))
    program.add_node(ComputeTask("c_1_1", 1, 1024))

    program.add_node(ProxyTask("x_1_1", 1))

    program.add_node(ComputeTask("c_1_2", 1, 1024))
    program.add_node(ComputeTask("c_1_3", 1, 1024))

    program.add_edge("s_0", "x_0_0")
    program.add_edge("x_0_0", "c_0_0")
    program.add_edge("x_0_0", "c_0_1")

    program.add_edge("c_0_0", "p_0")
    program.add_edge("c_0_1", "p_0")

    program.add_edge("c_0_0", "x_0_1")
    program.add_edge("c_0_1", "x_0_1")
    program.add_edge("p_0", "x_0_1")

    program.add_edge("x_0_1", "c_0_2")
    program.add_edge("x_0_1", "c_0_3")

    program.add_edge("c_0_2", "p_1")
    program.add_edge("c_0_3", "p_1")

    program.add_edge("s_1", "x_1_0")
    program.add_edge("p_0", "x_1_0")

    program.add_edge("x_1_0", "c_1_0")
    program.add_edge("x_1_0", "c_1_1")

    program.add_edge("c_1_0", "x_1_1")
    program.add_edge("c_1_1", "x_1_1")
    program.add_edge("p_1", "x_1_1")

    program.add_edge("x_1_1", "c_1_2")
    program.add_edge("x_1_1", "c_1_3")

    return program
