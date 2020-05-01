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


def test_negative_time():
    """
    Tests if negative delay is an error.
    """

    with pytest.raises(AssertionError):
        ComputeTask('c', 0, time=-100)


def test_negative_size():
    """
    Tests if negative size is an error.
    """

    with pytest.raises(AssertionError):
        ComputeTask('c', 0, size=-100)


def test_negative_node():
    """
    Tests if negative node is an error.
    """

    with pytest.raises(AssertionError):
        ComputeTask('c', -10, size=10)
