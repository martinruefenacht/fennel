"""

"""


import math


from fennel.core.program import Program
from fennel.core.tasks import StartTask, ProxyTask, PutTask, ComputeTask


def _target(ridx: int, process: int) -> int:
    """
    """

    smask = 2 ** ridx
    sbase = 2 ** (ridx+1)

    block = math.floor(process / sbase) * sbase
    offset = math.fmod(process + smask, sbase)

    return int(block + offset)


def generate_recursive_multiplying(processes: int, message_size: int) -> Program:
    """
    """

    # TODO needs to factor
    assert math.log2(processes).is_integer()
    assert message_size >= 0

    program = Program()

    # generate start nodes + proxies
    for process in range(processes):
        program.add_node(f's{process}',
                         StartTask(f's{process}', process))

        program.add_node(f'x_{process}_0',
                         ProxyTask(f'x_{process}_0', process))

        program.add_edge(f's{process}', f'x_{process}_0')

    rounds = int(math.log2(processes))
    for ridx in range(rounds):
        for process in range(processes):
            proxy_name = f'x_{process}_{ridx+1}'
            compute_name = f'c_{process}_{ridx}'
            put_name = f'p_{process}_{ridx}'

            # generate put
            target = _target(ridx, process)

            program.add_node(put_name,
                             PutTask(put_name, process, target, message_size))

            program.add_edge(put_name, f'c_{target}_{ridx}')
            program.add_edge(f'x_{process}_{ridx}', put_name)

            # generate proxy
            program.add_node(proxy_name, ProxyTask(proxy_name, process))

            # generate compute
            program.add_node(compute_name,
                             ComputeTask(compute_name, process, message_size))

            program.add_edge(f'x_{process}_{ridx}', compute_name)
            program.add_edge(compute_name, f'x_{process}_{ridx+1}')

    return program
