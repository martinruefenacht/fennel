"""

"""


import pytest


from fennel.tasks.sleep import SleepTask


def test_sleep_task():
    """
    """

    task = SleepTask('sleep', 0, 100)

    assert task.name == 'sleep'
    assert task.node == 0
    assert task.delay == 100


def test_sleep_input_exceptions():
    """
    Tests for erroneous constructor exception behaviour.
    """

    with pytest.raises(RuntimeError):
        SleepTask("test", 0)

    with pytest.raises(ValueError):
        SleepTask("test", 0, delay=0)

    with pytest.raises(ValueError):
        SleepTask("test", 0, until=0)


def test_sleep_getters():
    """
    tests SleepTask getters.
    """

    task = SleepTask("test", 0, delay=100)
    assert task.delay == 100

    task = SleepTask("test", 0, until=100)
    assert task.until == 100
