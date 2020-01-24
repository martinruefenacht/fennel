"""
"""


import logging

from fennel.core.program import Program
from fennel.tasks.compute import ComputeTask
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask

from fennel.core.machine import Machine
from fennel.computes.gamma import GammaModel


def test_any_between_two():
    """
    Tests whether the Any propery
    """

    prog = Program()

    prog.add_node(StartTask('s0', 0))
    prog.add_node(StartTask('s1', 1))

    c0 = ComputeTask('c0', 0, 50)
    prog.add_node(c0)

    c1 = ComputeTask('c1', 1, 100)
    prog.add_node(c1)

    c2 = ComputeTask('c2', 0, 100)
    c2.any = 1
    prog.add_node(c2)

    c3 = ComputeTask('c3', 1, 100)
    prog.add_node(c3)

    prog.add_edge('s0', 'c0')
    prog.add_edge('s1', 'c1')

    prog.add_edge('c0', 'c2')
    prog.add_edge('c1', 'c2')

    prog.add_edge('c0', 'c3')
    prog.add_edge('c1', 'c3')

    # machine
    machine = Machine(2, 1, GammaModel(0.1), None)
    machine.run(prog)

    assert machine.maximum_time > 0
