#!/usr/bin/env python3
'''
AppTasking - Inter Process Communications

Copyright (C) 2026 Jason Piszcyk
Email: Jason.Piszcyk@gmail.com

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (See file: COPYING). If not, see
<https://www.gnu.org/licenses/>.
'''
###########################################################################
#
# Imports
#
###########################################################################
from __future__ import annotations

# Shared variables, constants, etc

# System Modules
import threading
import queue
import multiprocessing
import multiprocessing.synchronize

# Local app modules

# Imports for python variable type hints
from typing import Callable


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#

#
# Constants
#

#
# Global Variables
#

###########################################################################
#
# Internal Functions
#
###########################################################################
#
# _create_event
#
def _create_event(
        task_type: str = "process"
) -> multiprocessing.synchronize.Event | threading.Event:
    '''
    Create an event suitable for the task_type

    Args:
        task_type (str): The type of task ("thread", "process")
            to be supported by this Queuing instance. "process" works
            with both threads and processes so is safer, but has more
            overhead

    Returns:
        Event: An event

    Raises:
        TypeError
            When task_type is not valid
    '''
    if task_type == "thread":
        return threading.Event()

    elif task_type == "process":
        return multiprocessing.Event()

    else:
        raise TypeError("task_type is invalid")


#
# _create_lock
#
def _create_lock(
        task_type: str = "process"
) -> multiprocessing.synchronize.Lock | threading.Lock:
    '''
    Create a Lock suitable for the task_type

    Args:
        task_type (str): The type of task ("thread", "process")
            to be supported by this Queuing instance. "process" works
            with both threads and processes so is safer, but has more
            overhead

    Returns:
        Lock: A lock

    Raises:
        TypeError:
            When task_type is not valid
    '''
    if task_type == "thread":
        return threading.Lock()

    elif task_type == "process":
        return multiprocessing.Lock()

    else:
        raise TypeError("task_type is invalid")


#
# _create_barrier
#
def _create_barrier(
        task_type: str = "process",
        parties: int = 2,
        action: Callable | None = None,
        timeout: float = 5.0
) -> multiprocessing.synchronize.Barrier | threading.Barrier:
    '''
    Create a Barrier suitable for the task_type

    Args:
        task_type (str): The type of task ("thread", "process")
            to be supported by this Queuing instance. "process" works
            with both threads and processes so is safer, but has more
            overhead
        parties (int): Number of parties required to wait before the
            barrier is lifted
        action (Callable): Function to be executed (by one of the
            waiting parties) when the barrier is lifted
        timeout (float): Time to wait for the barrier to be lifted

    Returns:
        Barrier: A Barrier

    Raises:
        TypeError:
            When task_type is not valid
    '''
    if task_type == "thread":
        return threading.Barrier(
            parties=parties,
            action=action,
            timeout=timeout
        )

    elif task_type == "process":
        return multiprocessing.Barrier(
            parties=parties,
            action=action,
            timeout=timeout
        )

    else:
        raise TypeError("task_type is invalid")


#
# _create_queue
#
def _create_queue(
        task_type: str = "process"
) -> multiprocessing.Queue | queue.Queue:
    '''
    Create a Queue suitable for the provided task_type

    Args:
        task_type (str): The type of task ("thread", "process")
            to be supported by this Queuing instance. "process" works
            with both threads and processes so is safer, but has more
            overhead

    Returns:
        Queue: An instance of a Taskqueue

    Raises:
        TypeError
            When task_type is not valid
    '''
    if task_type == "thread":
        return queue.Queue()

    elif task_type == "process":
        return multiprocessing.Queue()

    else:
        raise TypeError("task_type is invalid")


###########################################################################
#
# In case this is run directly rather than imported...
#
###########################################################################
'''
Handle case of being run directly rather than imported
'''
if __name__ == "__main__":
    pass
