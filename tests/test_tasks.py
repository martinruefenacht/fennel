"""

"""


from fennel.tasks.sleep import SleepTask
from fennel.tasks.compute import ComputeTask
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.put import PutTask


def test_sleep_task():
    """
    """

    task = SleepTask('sleep', 0, 100)

    assert task.name == 'sleep'
    assert task.node == 0
    assert task.delay == 100


def test_start_task():
    """
    """

    task = StartTask('start', 0)

    assert task.name == 'start'
    assert task.node == 0


def test_put_task():
    """
    """

    task = PutTask('put', 0, 1, 100)

    assert task.name == 'put'
    assert task.node == 0
    assert task.target == 1
    assert task.message_size == 100
    assert task.blocking

