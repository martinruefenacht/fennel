"""
Module for generators of point-to-point programs.
"""


import math
from pprint import pprint


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

        prog.add_node(ProxyTask(f'x_{cidx}', cidx))

        prog.add_edge(f's_{cidx}', f'x_{cidx}')

    # create put nodes
    for cidx in range(1, nodes):
        prog.add_node(PutTask(f'p0_{cidx}', 0, cidx, message_size))

        prog.add_edge(f's_{cidx}', f'p0_{cidx}')

        prog.add_edge('s_0', f'p0_{cidx}')
        prog.add_edge(f'p0_{cidx}', f'x_{cidx}')

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


def _generate_send_partition_block(size: int,
                                   partitions: int,
                                   threshold: int,
                                   round: int,
                                   program: Program
                                   ) -> None:
    """
    """

    # start sentinels
    program.add_node(ProxyTask(f'w_0_{round}_l', 0))
    program.add_node(ProxyTask(f'w_0_{round}_h', 0))

    program.add_edge(f'r_0_{round-1}_l', f'w_0_{round}_l')
    program.add_edge(f'r_0_{round-1}_h', f'w_0_{round}_h')

    program.add_node(ProxyTask(f'w_1_{round}_l', 1))
    program.add_node(ProxyTask(f'w_1_{round}_h', 1))

    program.add_edge(f'r_1_{round-1}_l', f'w_1_{round}_l')
    program.add_edge(f'r_1_{round-1}_h', f'w_1_{round}_h')

    # create puts
    # todo replace by puts
    p0_low = ProxyTask(f'p_0_{round}_l', 0)
    p0_low.any = threshold
    p0_low.concurrent = True
    program.add_node(p0_low)
    program.add_node(ProxyTask(f'p_0_{round}_h', 0))

    program.add_edge(f'p_0_{round}_l', f'w_1_{round}_l')
    program.add_edge(f'p_0_{round}_h', f'w_1_{round}_h')

    p1_low = ProxyTask(f'p_1_{round}_l', 1)
    p1_low.any = threshold
    p1_low.concurrent = True
    program.add_node(p1_low)
    program.add_node(ProxyTask(f'p_1_{round}_h', 1))

    # receive sentinels
    program.add_node(ProxyTask(f'r_0_{round}_l', 0))
    program.add_node(ProxyTask(f'r_0_{round}_h', 0))

    program.add_node(ProxyTask(f'r_1_{round}_l', 1))
    program.add_node(ProxyTask(f'r_1_{round}_h', 1))

    program.add_edge(f'p_1_{round}_l', f'r_0_{round}_l')
    program.add_edge(f'p_1_{round}_h', f'r_0_{round}_h')

    program.add_edge(f'p_1_{round}_l', f'r_1_{round}_l')
    program.add_edge(f'p_1_{round}_h', f'r_1_{round}_h')

    # computes
    for partition in range(partitions):
        program.add_node(ComputeTask(f'c_0_{round}_{partition}', 0, size))
        program.add_node(ComputeTask(f'c_1_{round}_{partition}', 1, size))

        if partition < threshold:
            # connect to low w
            program.add_edge(f'w_0_{round}_l', f'c_0_{round}_{partition}')
            program.add_edge(f'w_1_{round}_l', f'c_1_{round}_{partition}')

        else:
            # connect to high w
            program.add_edge(f'w_0_{round}_h', f'c_0_{round}_{partition}')
            program.add_edge(f'w_1_{round}_h', f'c_1_{round}_{partition}')

        # connect to puts
        program.add_edge(f'c_0_{round}_{partition}', f'p_0_{round}_l')
        program.add_edge(f'c_0_{round}_{partition}', f'p_0_{round}_h')

        program.add_edge(f'c_1_{round}_{partition}', f'p_1_{round}_l')
        program.add_edge(f'c_1_{round}_{partition}', f'p_1_{round}_h')


def generate_send_partitioned_p2p(size: int,
                                  partitions: int,
                                  threshold: int,
                                  rounds: int
                                  ) -> Program:
    """
    Generate a partitioned single threshold compute+put cycle.
    """

    assert size >= 0
    assert partitions > 0
    assert 0 < threshold < partitions
    assert rounds > 0

    # total size = partitions * message_size

    program = Program()

    program.add_node(StartTask('s_0', 0))
    program.add_node(StartTask('s_1', 1))

    program.add_node(ProxyTask('r_0_0_l', 0))
    program.add_node(ProxyTask('r_0_0_h', 0))

    program.add_edge('s_0', 'r_0_0_l')
    program.add_edge('s_0', 'r_0_0_h')

    program.add_node(ProxyTask('r_1_0_l', 1))
    program.add_node(ProxyTask('r_1_0_h', 1))
    program.add_edge('s_1', 'r_1_0_l')
    program.add_edge('s_1', 'r_1_0_h')

    for ridx in range(1, rounds+1):
        _generate_send_partition_block(size, partitions, threshold, ridx, program)

    pprint(program._metadata)
    pprint(program._edges_in)
    pprint(program._edges_out)

    return program
