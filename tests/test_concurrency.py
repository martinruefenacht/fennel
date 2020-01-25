"""
Tests concurrent programs and machines.
"""


# pylint: disable=redefined-outer-name


import pytest


from fennel.core.program import Program
from fennel.core.machine import Machine


from fennel.tasks.start import StartTask
from fennel.tasks.compute import ComputeTask
from fennel.tasks.proxy import ProxyTask
from fennel.computes.gamma import GammaModel


@pytest.fixture
def concurrent_compute_program():
    """
    Generates a concurrent compute program.
    """
    program = Program()

    program.add_node(StartTask('s0', 0))

    # these should overlap for total time 100
    program.add_node(ComputeTask('c0', 0, time=100, concurrent=True))
    program.add_node(ComputeTask('c1', 0, time=10, concurrent=True))

    program.add_node(ProxyTask('x0', 0))

    program.add_edge('s0', 'c0')
    program.add_edge('s0', 'c1')

    program.add_edge('c0', 'x0')
    program.add_edge('c1', 'x0')

    return program


def test_concurrent_on_non_concurrent(concurrent_compute_program):
    """
    Tests whether a concurrent program on a non concurrent machine
    executes correcrtly.
    """

    nodes = 1
    processes = 1

    machine = Machine(nodes, processes, GammaModel(1), None)
    machine.run(concurrent_compute_program)

    assert machine.maximum_time == 110


def test_concurrent_compute(concurrent_compute_program):
    """
    Tests whether a concurrent computation works.
    """

    # two processes required for concurrency
    machine = Machine(1, 2, GammaModel(1), None)
    machine.run(concurrent_compute_program)

    assert machine.maximum_time == 100
