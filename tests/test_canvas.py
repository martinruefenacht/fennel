"""
Collection of tests for drawing the Canvas of a network simulation.
"""

from pathlib import Path
import re


from fennel.visual.canvas import Canvas
from fennel.core.machine import Machine
from fennel.networks.lbmodel import LBModel
from fennel.computes.gamma import GammaModel
from fennel.generators.p2p import generate_send


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
