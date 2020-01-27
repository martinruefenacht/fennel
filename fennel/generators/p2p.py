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
    wait_primary_low = f'w_0_{round}_l'
    wait_primary_high = f'w_0_{round}_h'

    wait_secondary_low = f'w_1_{round}_l'
    wait_secondary_high = f'w_1_{round}_h'

    recv_primary_low = f'r_0_{round-1}_l'
    recv_primary_high = f'r_0_{round-1}_h'

    recv_secondary_low = f'r_1_{round-1}_l'
    recv_secondary_high = f'r_1_{round-1}_h'

    program.add_node(ProxyTask(wait_primary_low, 0))
    program.add_node(ProxyTask(wait_primary_high, 0))

    program.add_edge(recv_primary_low, wait_primary_low)
    program.add_edge(recv_primary_high, wait_primary_high)

    program.add_node(ProxyTask(wait_secondary_low, 1))
    program.add_node(ProxyTask(wait_secondary_high, 1))

    program.add_edge(recv_secondary_low, wait_secondary_low)
    program.add_edge(recv_secondary_high, wait_secondary_high)

    # create puts
    # todo replace by puts
    put_primary_low = f'p_0_{round}_l'
    put_primary_high = f'p_0_{round}_h'

    p0_low = ProxyTask(put_primary_low, 0)
    p0_low.any = threshold
    p0_low.concurrent = True
    program.add_node(p0_low)
    program.add_node(ProxyTask(put_primary_high, 0))

    program.add_edge(put_primary_low, wait_secondary_low)
    program.add_edge(put_primary_high, wait_secondary_high)

    put_secondary_low = f'p_1_{round}_l'
    put_secondary_high = f'p_1_{round}_h'

    p1_low = ProxyTask(put_secondary_low, 1)
    p1_low.any = threshold
    p1_low.concurrent = True
    program.add_node(p1_low)
    program.add_node(ProxyTask(put_secondary_high, 1))

    # receive sentinels
    recv_primary_low = f'r_0_{round}_l'
    recv_primary_high = f'r_0_{round}_h'

    recv_secondary_low = f'r_1_{round}_l'
    recv_secondary_high = f'r_1_{round}_h'

    program.add_node(ProxyTask(recv_primary_low, 0))
    program.add_node(ProxyTask(recv_primary_high, 0))

    program.add_node(ProxyTask(recv_secondary_low, 1))
    program.add_node(ProxyTask(recv_secondary_high, 1))

    program.add_edge(put_secondary_low, recv_primary_low)
    program.add_edge(put_secondary_high, recv_primary_high)

    program.add_edge(put_secondary_low, recv_secondary_low)
    program.add_edge(put_secondary_high, recv_secondary_high)

    # computes
    for partition in range(partitions):
        compute_primary = f'c_0_{round}_{partition}'
        program.add_node(ComputeTask(compute_primary,
                                     0, size, concurrent=True))

        compute_secondary = f'c_1_{round}_{partition}'
        program.add_node(ComputeTask(compute_secondary,
                                     1, size, concurrent=True))

        if partition < threshold:
            # connect to low w
            program.add_edge(wait_primary_low, compute_primary)
            program.add_edge(wait_secondary_low, compute_secondary)

        else:
            # connect to high w
            program.add_edge(wait_primary_high, compute_primary)
            program.add_edge(wait_secondary_high, compute_secondary)

        # connect to puts
        program.add_edge(compute_primary, put_primary_low)
        program.add_edge(compute_primary, put_primary_high)

        program.add_edge(compute_secondary, put_secondary_low)
        program.add_edge(compute_secondary, put_secondary_high)


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
        _generate_send_partition_block(size, partitions, threshold,
                                       ridx, program)

    pprint(program._metadata)
    pprint(program._edges_in)
    pprint(program._edges_out)

    return program
