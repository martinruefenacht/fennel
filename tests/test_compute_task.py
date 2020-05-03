"""
Tests with respect to the compute task.
"""


import pytest
from hypothesis import given
from hypothesis.strategies import integers

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

    with pytest.raises(RuntimeError):
        ComputeTask("test", 0, size=1, time=1)

    with pytest.raises(ValueError):
        ComputeTask("test", 0, size=0)

    with pytest.raises(ValueError):
        ComputeTask("test", 0, time=0)

    with pytest.raises(ValueError):
        ComputeTask("test", -10, 100)


def test_compute_repr():
    """
    Tests representation of a ComputeTask.
    """

    assert repr(ComputeTask("test", 0, size=10)) == "compute test size 10"
    assert repr(ComputeTask("test", 0, time=10)) == "compute test time 10"


@given(integers(min_value=1))
def test_getter_size(size: int):
    """
    """

    task = ComputeTask("task", 0, size=size)
    assert task.size == size


@given(integers(min_value=1))
def test_getter_time(time: int):
    """
    """

    task = ComputeTask("task", 0, time=time)
    assert task.time == time
