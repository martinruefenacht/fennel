"""
Tests with respect to the compute task.
"""


import pytest


from fennel.tasks.compute import ComputeTask
from fennel.computes.gamma import GammaModel


@pytest.mark.parametrize(
    'model',
    [GammaModel(0.0)],
    ids=lambda model: model.__class__)
def test_fixed_compute(model):
    """
    Tests whether a fixed time compute task is correctly simulated.
    """

    delay = 100

    task = ComputeTask('c', 0, time=delay)
    assert model.evaluate(0, task) == delay


def test_compute_input_exceptions():
    """
    Tests the ComputeTask for the correct exception behaviour.
    """

    with pytest.raises(RuntimeError):
        ComputeTask("test", 0)

    with pytest.raises(ValueError):
        ComputeTask("test", 0, size=0)

    with pytest.raises(ValueError):
        ComputeTask("test", 0, time=0)

    with pytest.raises(ValueError):
        ComputeTask("test", -1, 100)


def test_compute_repr():
    """
    Tests representation of a ComputeTask.
    """

    assert repr(ComputeTask("test", 0, size=10)) == "compute test size 10"
    assert repr(ComputeTask("test", 0, time=10)) == "compute test time 10"


def test_setters():
    """
    Tests ComputeTask setters.
    """

    task = ComputeTask("test", 0, time=100)

    task.time = 200
    assert task.time == 200

    task = ComputeTask("test", 0, size=100)

    task.size = 200
    assert task.size == 200
