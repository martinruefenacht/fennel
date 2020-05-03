"""
Collection of tests for drawing the Canvas of a network simulation.
"""

from pathlib import Path
import re


import pytest


from fennel.visual.canvas import Canvas
from fennel.core.machine import Machine
from fennel.networks.lbmodel import LBModel
from fennel.networks.lbpmodel import LBPModel
from fennel.computes.gamma import GammaModel

import fennel.generators.p2p as p2p
import fennel.generators.allreduce as allreduce
import fennel.generators.allgather as allgather
import fennel.generators.compute as compute
import fennel.generators.bsp as bsp

pytestmark = pytest.mark.canvas


def compare_eps_files(reference: Path, newest: Path) -> bool:
    """
    Compare the two given EPS files.
    """

    patterns = [
        r"%%CreationDate:.*?\n",
        r"\n.*?pattern\d+.*?\n",
        ]

    tests = []

    for path in (reference, newest):
        with path.open() as data:
            eps = data.read()

            for pattern in patterns:
                eps = re.sub(pattern, "", eps)

            tests.append(eps)

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

    program = p2p.send(10, True)

    canvas = Canvas()

    machine = Machine(2, 1, GammaModel(0), LBModel(latency, 0))
    machine.canvas = canvas
    machine.run(program)

    canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_send_compute(shared_datadir):
    """
    """

    name = "send_compute.eps"
    latency = 300

    path = Path().cwd() / "tests/" / name

    program = p2p.send(10, False)
    program2 = compute.simple_compute(1024)

    canvas = Canvas()

    machine = Machine(2, 1, GammaModel(0.1), LBPModel(latency, 0.1, 100))
    machine.canvas = canvas
    machine.run(program)
    machine.run(program2)

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

    program = p2p.multicast(1, 2, False)
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

    program = allreduce.generate_recursive_doubling(8, 100)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_pm_rd_allgather(shared_datadir):
    """
    Tests the postal model recursive doubling allgather algorithm drawing.
    """

    name = "pm_rd_allgather.eps"
    latency = 100
    bandwidth = 0.02
    nodes = 8
    msgsize = 4096

    path = Path.cwd() / "tests" / name

    machine = Machine(nodes, 1, GammaModel(1), LBModel(latency, bandwidth))
    machine.canvas = Canvas()

    program = allgather.recursive_doubling(nodes, msgsize)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_simple_compute(shared_datadir):
    """
    Tests a simple compute program and a gamma compute model.
    """

    name = "compute.eps"
    msgsize = 1024
    rounds = 5
    gamma = 0.05

    path = Path.cwd() / "tests" / name

    machine = Machine(1, 1, GammaModel(gamma), LBModel(0, 0))
    machine.canvas = Canvas()

    program = compute.simple_compute(msgsize, rounds)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_bsp_single(shared_datadir):
    """
    Tests the BSP single compute + barriers.
    """

    name = "bsp_single.eps"
    nodes = 4
    msgsize = 1024
    gamma = 0.1
    rounds = 2

    path = Path.cwd() / "tests" / name

    machine = Machine(nodes, 1, GammaModel(gamma), LBModel(0, 0))
    machine.canvas = Canvas()

    program = bsp.single_superstep(nodes, msgsize, rounds)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_allgather_ring(shared_datadir):
    """
    Tests whether the AllGather ring is correctly drawn.
    """

    name = "pm_allgather_ring.eps"
    nodes = 4
    msgsize = 1024
    gamma = 0.1
    latency = 100
    bandwidth = 0.1

    path = Path.cwd() / "tests" / name

    machine = Machine(nodes, 1, GammaModel(gamma), LBModel(latency, bandwidth))
    machine.canvas = Canvas()

    program = allgather.ring(nodes, msgsize)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_fetch(shared_datadir):
    """
    Tests the GetTask and fetch generator.
    """

    name = "pm_fetch.eps"
    nodes = 2
    msgsize = 1024
    gamma = 0.1
    latency = 100
    bandwidth = 0.1

    path = Path.cwd() / "tests" / name

    machine = Machine(nodes, 1, GammaModel(gamma), LBModel(latency, bandwidth))
    machine.canvas = Canvas()

    program = p2p.fetch(msgsize, False)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)


def test_rat(shared_datadir):
    """
    """

    name = "pm_rat.eps"
    nodes = 2
    msgsize = 1024
    gamma = 0.1
    latency = 100
    bandwidth = 0.1

    path = Path.cwd() / "tests" / name

    machine = Machine(nodes, 1, GammaModel(gamma), LBModel(latency, bandwidth))
    machine.canvas = Canvas()

    program = p2p.request_response_transfer_ack(msgsize)

    machine.run(program)
    machine.canvas.write(str(path))

    assert compare_eps_files(shared_datadir / name, path)
