"""
Tests whether basic properties work.
"""


import logging


import pytest


from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel


def test_start_proxy():
    """
    Tests whether the Any propery
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))
    prog.add_node(ProxyTask('x0', 0))

    prog.add_edge('s0', 'x0')

    # machine
    machine = Machine(1, 1, None, None)
    machine.run(prog)

    assert machine


def test_start_compute_proxy():
    """
    Tests whether the Any propery
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))
    prog.add_node(ComputeTask('c0', 0, 100))
    prog.add_node(ProxyTask('x0', 0))

    prog.add_edge('s0', 'c0')
    prog.add_edge('c0', 'x0')

    # machine
    machine = Machine(1, 1, GammaModel(1), None)
    machine.run(prog)

    assert machine


def test_proxy_end_requirement():
    """
    Tests whether it correctly raises an error when the final task at the end
    of the DAG is not a ProxyTask.
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))
    prog.add_node(ComputeTask('c0', 0, 100))

    prog.add_edge('s0', 'c0')

    # machine
    machine = Machine(1, 1, GammaModel(1), None)

    with pytest.raises(RuntimeError):
        machine.run(prog)


def test_any_property():
    """
    Tests whether the any property functions.
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))

    # never executed
    prog.add_node(ProxyTask('x0', 0))

    c0 = ComputeTask('c0', 0, 100)
    c0.any = 1
    prog.add_node(c0)
    prog.add_node(ProxyTask('x1', 0))

    prog.add_edge('s0', 'c0')
    prog.add_edge('x0', 'c0')
    prog.add_edge('c0', 'x1')

    # machine
    machine = Machine(1, 1, GammaModel(1), None)
    machine.run(prog)

    assert machine.is_finished()


def test_all_property():
    """
    Tests whether the any property functions.
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))

    # never executed
    prog.add_node(ProxyTask('x0', 0))

    prog.add_node(ComputeTask('c0', 0, 100))
    prog.add_node(ProxyTask('x1', 0))

    prog.add_edge('s0', 'c0')
    prog.add_edge('x0', 'c0')
    prog.add_edge('c0', 'x1')

    # machine
    machine = Machine(1, 1, GammaModel(1), None)
    machine.run(prog)

    assert not machine.is_finished()
