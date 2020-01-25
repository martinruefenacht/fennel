"""
Tests partitioned behaviour, any property, and concurrent computation.
"""


# pylint: disable=redefined-outer-name


import logging


from fennel.core.program import Program
from fennel.core.machine import Machine


from fennel.tasks.start import StartTask
from fennel.tasks.compute import ComputeTask
from fennel.tasks.proxy import ProxyTask
from fennel.computes.gamma import GammaModel


def test_partitioned_pattern():
    """
    """

    # generate partitioned program
    program = Program()

    program.add_node(StartTask('s0', 0))
    program.add_node(StartTask('s1', 1))

    # these should overlap for total time 100
    program.add_node(ComputeTask('c0', 0, time=100, concurrent=True))
    program.add_node(ComputeTask('c1', 0, time=10, concurrent=True))
    program.add_node(ComputeTask('c2', 0, time=20, concurrent=True))

    program.add_node(ProxyTask('x0', 0))
    x1 = ProxyTask('x1', 0)
    x1.any = 2
    x1.concurrent = True
    program.add_node(x1)
    program.add_node(ProxyTask('x2', 1))

    program.add_edge('s0', 'c0')
    program.add_edge('s0', 'c1')
    program.add_edge('s0', 'c2')

    program.add_edge('c0', 'x0')
    program.add_edge('c1', 'x0')
    program.add_edge('c2', 'x0')

    program.add_edge('c0', 'x1')
    program.add_edge('c1', 'x1')
    program.add_edge('c2', 'x1')

    program.add_edge('s1', 'x2')
    program.add_edge('x1', 'x2')

    machine = Machine(2, 3, GammaModel(1), None)
    machine.run(program)

    logging.info(machine._node_times)

    assert all(process <= 10 for process in machine._node_times[1])
    assert all(process <= 100 for process in machine._node_times[0])
