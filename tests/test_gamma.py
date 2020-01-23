"""
"""

import pytest
from hypothesis import given
from hypothesis.strategies import floats


from fennel.computes.gamma import GammaModel


@given(floats(0.0))
def test_gamma_init(gamma):
    """
    """

    model = GammaModel(gamma)

    assert model.gamma == gamma


@given(floats(max_value=0.0, exclude_max=True))
def test_negative_gamma_fails(gamma):
    """
    """

    with pytest.raises(RuntimeError):
        model = GammaModel(gamma)

        assert model.gamma == gamma
