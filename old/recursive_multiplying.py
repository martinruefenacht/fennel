"""

"""


from typing import Iterable, Optional, Any, Tuple
from itertools import tee
import logging


from fennel.core.program import Program
from fennel.tasks.start import StartTask
from fennel.tasks.proxy import ProxyTask
from fennel.tasks.put import PutTask
from fennel.tasks.compute import ComputeTask


def _pairwise(iterable: Iterable[Any]) -> Iterable[Tuple[Any, Any]]:
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    primary, secondary = tee(iterable)
    next(secondary, None)
    return zip(primary, secondary)


def _prime_factorization(num: int) -> Iterable[int]:
    """
    Find prime factorization of non-zero positive number.
    """

    assert num > 0

    step = 2
    factors = []

    while step * step <= num:
        if num % step:
            step += 1
        else:
            num //= step
            factors.append(step)

    if num > 1:
        factors.append(num)

    return sorted(factors)


def _aggregate_factors(factors: Iterable[int],
                       threshold: int
                       ) -> Iterable[int]:
    """
    """

    if len(factors) <= 1:
        return factors

    factors = sorted(factors)

    prod = factors[0] * factors[1]
    if prod > threshold:
        return factors

    return _aggregate_factors([prod] + factors[2:], threshold)


def _target(base: int, mask: int, process: int, index: int) -> int:
    """
    Calculate target in recursive multiplying group.
    """

    sub_mask = (index + 1) * mask
    block = process // base
    offset = (process + sub_mask) % base

    return block + offset


def generate_recursive_multiplying(processes: int,
                                   message_size: int,
                                   aggregate: Optional[int] = None
                                   ) -> Program:
    """
    Generate a factored recursive multiplying schedule.
    """

    assert processes >= 1
    assert _prime_factorization(processes)
    assert message_size >= 0

    program = Program()

    # generate start nodes + proxies
    for process in range(processes):
        program.add_node(f's{process}',
                         StartTask(f's{process}', process))

        program.add_node(f'x_{process}_0',
                         ProxyTask(f'x_{process}_0', process))

        program.add_edge(f's{process}', f'x_{process}_0')

    factorization = _prime_factorization(processes)
    logging.debug('processes %i prime factorization %i',
                  processes, factorization)

    # aggregate schedule to target
    if aggregate:
        factorization = _aggregate_factors(factorization, aggregate)

    mask = 1
    for ridx, factor in enumerate(factorization):
        base = factor * mask

        for process in range(processes):
            # generate proxy
            proxy_name = f'x_{process}_{ridx+1}'
            program.add_node(proxy_name, ProxyTask(proxy_name, process))

            # multicast send
            for index in range(factor - 1):
                # generate put
                put_name = f'p_{process}_{ridx}_{index}'

                target = _target(base, mask, process, index)

                program.add_node(put_name,
                                 PutTask(put_name, process,
                                         target, message_size))

                program.add_edge(put_name, f'c_{target}_{ridx}')
                program.add_edge(f'x_{process}_{ridx}', put_name)

            # generate compute
            compute_name = f'c_{process}_{ridx}'
            program.add_node(compute_name,
                             ComputeTask(compute_name, process, message_size))

            program.add_edge(f'x_{process}_{ridx}', compute_name)
            program.add_edge(compute_name, f'x_{process}_{ridx+1}')

        mask *= factor

    return program
