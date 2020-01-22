"""
Compute related tasks
"""


import pytest


from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel
from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.compute import ComputeTask


@pytest.fixture
def single_compute_program() -> Program:
    """
    Generates a single compute task program.
    """

    size = 1

    program = Program()
    program.add_node(StartTask('s', 0))
    program.add_node(ComputeTask('c', 0, size))
    program.add_node(ProxyTask('x', 0))
    program.add_edge('s', 'c')
    program.add_edge('c', 'x')

    return program


def test_compute_single(single_compute_program: Program):
    """
    Tests whether a single compute task on a single node with
    a single process with a gamma model functions.
    """

    gamma = 1

    compute = GammaModel(gamma)

    machine = Machine(1, 1, compute, None)

    machine.run(single_compute_program)

    size = single_compute_program.get_task('c').size
    assert machine.maximum_time == gamma * size
