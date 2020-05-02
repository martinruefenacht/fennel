"""
A collection of tests for the Machine class.
"""


from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel
from fennel.networks.lbmodel import LBModel
import fennel.generators.p2p as p2p


def test_machine_sequential_programs():
    """
    Tests whether the machine correctly runs multiple sequential programs.
    """

    latency = 100

    machine = Machine(2, 1, GammaModel(0), LBModel(latency, 0))

    program_1 = p2p.pingpong(8, 1)
    program_2 = p2p.pingpong(8, 1)

    machine.run(program_1)
    machine.run(program_2)

    assert machine.maximum_time == latency * 4
