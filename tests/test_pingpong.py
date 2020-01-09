"""
Verifies all LB machines.
"""


from fennel.generators.p2p import generate_pingpong
from fennel.machines.lbmachine import LBMachine, LBPMachine


def test_pingpong_lbmachine():
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


def test_pingpong_lbpmachine():
    """
    Test LBPMachine with a PingPong program.
    """

    nodes = 2
    msg_size = 0
    rounds = 1

    latency = 1000
    bandwidth = 0
    pipeline = 0
    compute = 0

    program = generate_pingpong(msg_size, rounds)

    machine = LBPMachine(nodes, latency, bandwidth, pipeline, compute)
    machine.run(program)

    assert machine.maximum_time == rounds * 2 * latency
