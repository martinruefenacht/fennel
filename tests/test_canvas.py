"""
Collection of tests for drawing the Canvas of a network simulation.
"""

from pathlib import Path
import re


from fennel.visual.canvas import Canvas
from fennel.core.machine import Machine
from fennel.networks.lbmodel import LBModel
from fennel.networks.lbpmodel import LBPModel
from fennel.computes.gamma import GammaModel
from fennel.generators.p2p import generate_send, generate_multicast
from fennel.generators.allreduce import generate_recursive_doubling


def compare_eps_files(reference: Path, newest: Path) -> bool:
    """
    Compare the two given EPS files.
    """

    pattern = r"%%CreationDate:.*?\n"

    tests = []

    for path in (reference, newest):
        with path.open() as data:
            tests.append(hash(re.sub(pattern, "", data.read())))

    return all(test == tests[0] for test in tests)


def test_empty_canvas(shared_datadir):
    """
    Draws an empty machine.
    """

    name = "empty.eps"
    path = Path().cwd() / "tests/" / name

    canvas = Canvas()
    canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_send_canvas(shared_datadir):
    """
    Draws a single send on a LBmachine.
    """

    name = "send.eps"
    latency = 100

    path = Path().cwd() / "tests/" / name

    program = generate_send(10, True)

    canvas = Canvas()

    machine = Machine(2, 1, GammaModel(0), LBModel(latency, 0))
    machine.canvas = canvas
    machine.run(program)

    canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_lbpmachine_multicast(shared_datadir):
    """
    Tests if the pipelining postal model is correct with two sends.
    """

    name = "ppm_double_send.eps"
    latency = 500
    bandwidth = 0
    pipeline = 100

    path = Path().cwd() / "tests/" / name

    canvas = Canvas()

    machine = Machine(3, 1,
                      GammaModel(0),
                      LBPModel(latency, bandwidth, pipeline))
    machine.canvas = canvas

    program = generate_multicast(1, 2, False)
    machine.run(program)

    canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_pm_rd(shared_datadir):
    """
    Tests whether a recursive doubling pattern with a postal model
    machine is regression correct.
    """

    name = "pm_rd_allreduce.eps"
    latency = 200
    bandwidth = 0

    path = Path.cwd() / "tests" / name

    machine = Machine(8, 1, GammaModel(1), LBModel(latency, bandwidth))
    machine.canvas = Canvas()

    program = generate_recursive_doubling(8, 100)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)
