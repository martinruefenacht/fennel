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
from fennel.generators.compute import generate_compute


@pytest.fixture
def single_compute_program() -> Program:
    """
    Generates a single compute task program.
    """

    size = 1

    program = Program()
    program.add_node(StartTask('s', 0))
    program.add_node(ComputeTask('c', 0, size, False))
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


def test_single_process():
    """
    """

    program = generate_compute(1, 10, 10, False, 1)

    compute = GammaModel(1)

    machine = Machine(1, 1, compute, None)
    machine.run(program)

    assert machine.maximum_time == 100


def test_multi_process():
    """
    """

    program = generate_compute(1, 10, 10, True, 1)

    compute = GammaModel(1)

    machine = Machine(1, 2, compute, None)
    machine.run(program)

    assert machine.maximum_time == 50
