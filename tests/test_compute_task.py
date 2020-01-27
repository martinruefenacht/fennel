"""
Tests with respect to the compute task.
"""


import pytest


from fennel.tasks.compute import ComputeTask
from fennel.computes.gamma import GammaModel, NoisyGammaModel


@pytest.mark.parametrize('model', [GammaModel(0.0), NoisyGammaModel(0.0, 0.0)])
def test_fixed_compute(model):
    """
    Tests whether a fixed time compute task is correctly simulated.
    """

    delay = 100

    task = ComputeTask('c', 0, time=delay)
    assert model.evaluate(0, task) == delay
