"""
Verifies all LB machines.
"""


import math


from fennel.generators.p2p import generate_pingpong, generate_multicast
from fennel.generators.allreduce import generate_recursive_doubling
from fennel.machines.lbmachine import LBMachine


def test_lbmachine():
    """
    Test LBMachine with a PingPong program.
    """

    nodes = 2
    msg_size = 0
    rounds = 1

    latency = 1000
    bandwidth = 0
    compute = 0

    program = generate_pingpong(msg_size, rounds)

    machine = LBMachine(nodes, latency, bandwidth, compute)
    machine.run(program)

    assert machine.maximum_time == rounds * 2 * latency


def test_multicast_lbmachine():
    """
    Test LBMachine with a PingPong program.
    """

    nodes = 2
    msg_size = 0
    rounds = 1

    latency = 1000
    bandwidth = 0
    compute = 0

    program = generate_multicast(msg_size, rounds)

    machine = LBMachine(nodes, latency, bandwidth, compute)
    machine.run(program)

    assert machine.maximum_time == (nodes-1) * latency


def test_rd_lbmachine():
    """
    Test LBMachine with a PingPong program.
    """

    nodes = 8
    msg_size = 0
    # rounds = 1

    latency = 1000
    bandwidth = 0
    compute = 0

    program = generate_recursive_doubling(nodes, msg_size)

    machine = LBMachine(nodes, latency, bandwidth, compute)
    machine.run(program)

    assert machine.maximum_time == math.log2(nodes) * latency



