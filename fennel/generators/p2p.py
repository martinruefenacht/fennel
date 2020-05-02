"""
Module for generators of point-to-point programs.
"""


from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.put import PutTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.compute import ComputeTask


def send(
        message_size: int,
        blocking: bool,
        sender: int = 0,
        receiver: int = 1
        ) -> Program:
    """
    Generate a single send from rank 0 -> rank 1.
    """

    assert message_size >= 0

    prog = Program()

    # generate start tasks for all procs
    prog.add_node(StartTask(f's{sender}', sender, skew=100))
    prog.add_node(StartTask(f's{receiver}', receiver))

    # generate single put task for rank 0
    prog.add_node(PutTask('p', sender, receiver, message_size, block=blocking))

    # generate end tasks for all procs
    prog.add_node(ProxyTask(f'x{sender}', sender))
    prog.add_node(ProxyTask(f'x{receiver}', receiver))

    # rank 0 dependencies
    prog.add_edge(f's{sender}', 'p')
    prog.add_edge('p', f'x{sender}')

    # rank 1 dependencies
    prog.add_edge(f's{receiver}', f'x{receiver}')
    prog.add_edge('p', f'x{receiver}')

    return prog


def multicast(
        message_size: int,
        width: int,
        blocking: bool
        ) -> Program:
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
        prog.add_node(PutTask(f'p_{cidx}', 0, cidx,
                              message_size, block=blocking))

        prog.add_edge(f'p_{cidx}', f'x_{cidx}')
        prog.add_edge(f'p_{cidx}', f'x_0')
        prog.add_edge('s_0', f'p_{cidx}')

    return prog


def pingpong(
        message_size: int,
        rounds: int,
        sender: int = 0,
        receiver: int = 1
        ) -> Program:
    """
    Generate a ping pong program.
    """

    assert message_size >= 0
    assert rounds > 0

    prog = Program()

    prog.add_node(StartTask(f's{sender}', sender))
    prog.add_node(StartTask(f's{receiver}', receiver))

    prog.add_node(ProxyTask(f'x{sender}_0', sender))
    prog.add_node(ProxyTask(f'x{receiver}_0', receiver))

    prog.add_edge(f's{sender}', f'x{sender}_0')
    prog.add_edge(f's{receiver}', f'x{receiver}_0')

    for ridx in range(0, rounds):
        prog.add_node(PutTask(f'p{sender}_{ridx}', sender, receiver, message_size))
        prog.add_node(PutTask(f'p{receiver}_{ridx}', receiver, sender, message_size))

        prog.add_edge(f'x{sender}_{ridx}', f'p{sender}_{ridx}')
        prog.add_edge(f'x{receiver}_{ridx}', f'p{receiver}_{ridx}')

        prog.add_node(ProxyTask(f'x{sender}_{ridx+1}', sender))
        prog.add_node(ProxyTask(f'x{receiver}_{ridx+1}', receiver))

        prog.add_edge(f'p{sender}_{ridx}', f'x{sender}_{ridx+1}')
        prog.add_edge(f'p{receiver}_{ridx}', f'x{receiver}_{ridx+1}')

        # ping
        prog.add_edge(f'p{sender}_{ridx}', f'p{receiver}_{ridx}')

        # pong
        prog.add_edge(f'p{receiver}_{ridx}', f'x{sender}_{ridx+1}')

    return prog


def _generate_send_partition_block(size: int,
                                   partitions: int,
                                   threshold: int,
                                   rnd: int,
                                   program: Program
                                   ) -> None:
    """
    """

    # start sentinels
    wait_primary_low = f'w_0_{rnd}_l'
    wait_primary_high = f'w_0_{rnd}_h'

    wait_secondary_low = f'w_1_{rnd}_l'
    wait_secondary_high = f'w_1_{rnd}_h'

    recv_primary_low = f'r_0_{rnd-1}_l'
    recv_primary_high = f'r_0_{rnd-1}_h'

    recv_secondary_low = f'r_1_{rnd-1}_l'
    recv_secondary_high = f'r_1_{rnd-1}_h'

    program.add_node(ProxyTask(wait_primary_low, 0))
    program.add_node(ProxyTask(wait_primary_high, 0))

    program.add_edge(recv_primary_low, wait_primary_low)
    program.add_edge(recv_primary_high, wait_primary_high)

    program.add_node(ProxyTask(wait_secondary_low, 1))
    program.add_node(ProxyTask(wait_secondary_high, 1))

    program.add_edge(recv_secondary_low, wait_secondary_low)
    program.add_edge(recv_secondary_high, wait_secondary_high)

    # create puts
    put_primary_low = f'p_0_{rnd}_l'
    put_primary_high = f'p_0_{rnd}_h'

    p0_low = PutTask(put_primary_low, 0, 1, size*threshold)
    p0_low.any = threshold
    p0_low.concurrent = True
    program.add_node(p0_low)
    program.add_node(PutTask(put_primary_high, 0, 1, size))

    program.add_edge(put_primary_low, wait_secondary_low)
    program.add_edge(put_primary_high, wait_secondary_high)

    put_secondary_low = f'p_1_{rnd}_l'
    put_secondary_high = f'p_1_{rnd}_h'

    p1_low = PutTask(put_secondary_low, 1, 0, size*threshold)
    p1_low.any = threshold
    p1_low.concurrent = True
    program.add_node(p1_low)
    program.add_node(PutTask(put_secondary_high, 1, 0, size))

    # receive sentinels
    recv_primary_low = f'r_0_{rnd}_l'
    recv_primary_high = f'r_0_{rnd}_h'

    recv_secondary_low = f'r_1_{rnd}_l'
    recv_secondary_high = f'r_1_{rnd}_h'

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
        compute_primary = f'c_0_{rnd}_{partition}'
        program.add_node(ComputeTask(compute_primary,
                                     0, size, concurrent=True))

        compute_secondary = f'c_1_{rnd}_{partition}'
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


def send_partitioned(
        size: int,
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

    return program


def request_response_transfer_ack(
    message_size: int,
    rounds: int,
    sender: int = 0,
    receiver: int = 1
    ) -> Program:

    raise NotImplementedError
