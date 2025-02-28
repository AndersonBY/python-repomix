"""
Process Concurrency Module - Handles functionalities related to process concurrency
"""

import os
import sys
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from typing import Union

PoolExecutor = Union[ProcessPoolExecutor, ThreadPoolExecutor]


def _is_running_on_lambda() -> bool:
    """Check if running in AWS Lambda environment"""
    return bool(os.getenv("AWS_EXECUTION_ENV"))


def _get_concurrency_strategy() -> str:
    """Get the concurrency strategy

    Returns:
        'thread' or 'process'
    """
    # First check environment variable
    env_strategy = os.getenv("REPOMIX_COCURRENCY_STRATEGY", "").lower()
    if env_strategy in ("thread", "process"):
        return env_strategy

    # Then check if running in Lambda
    if _is_running_on_lambda():
        return "thread"

    # Default to process pool
    return "process"


def get_process_concurrency() -> PoolExecutor:
    """Get process pool or thread pool executor

    Returns:
        Instance of ProcessPoolExecutor or ThreadPoolExecutor
    """
    max_workers = _get_max_workers()
    strategy = _get_concurrency_strategy()

    if strategy == "thread":
        return ThreadPoolExecutor(max_workers=max_workers)
    return ProcessPoolExecutor(max_workers=max_workers)


def _get_max_workers() -> int:
    """Get the suggested number of concurrent processes"""
    # Get the number of CPU cores
    try:
        if sys.platform == 'linux':
            # Linux specific method
            cpu_count = len(os.sched_getaffinity(0))
        else:
            # Generic method for other platforms
            cpu_count = multiprocessing.cpu_count()
    except (AttributeError, NotImplementedError):
        cpu_count = 1

    # Use 75% of the CPU core count as a baseline, but not exceeding 32
    suggested = max(1, int(cpu_count * 0.75))
    return min(suggested, 32)


def get_chunk_size(total_items: int, num_processes: int) -> int:
    """Calculate the number of items each process should handle

    Args:
        total_items: Total number of items
        num_processes: Number of processes

    Returns:
        Number of items each process should handle
    """
    # Ensure each process handles at least 1 item
    return max(1, int(total_items / num_processes))


def distribute_work(items: list, num_processes: int) -> list[tuple[int, list]]:
    """Distribute work among multiple processes

    Args:
        items: List of items to be processed
        num_processes: Number of processes

    Returns:
        List of tuples containing process index and corresponding item lists
    """
    # Calculate the number of items per process
    chunk_size = get_chunk_size(len(items), num_processes)

    # Distribute work
    work_distribution = []
    for i in range(num_processes):
        start = i * chunk_size
        end = start + chunk_size if i < num_processes - 1 else len(items)
        if start < len(items):
            work_distribution.append((i, items[start:end]))

    return work_distribution
