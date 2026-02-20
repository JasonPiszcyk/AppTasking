#!/usr/bin/env python3
'''
Task Wrapper - wrapper to run the task function, to allow us to capture
state and result information

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
import sys
import traceback
import threading
import multiprocessing
import multiprocessing.synchronize
from applogging.logging import get_logger, init_console_logger

# Local app modules
from apptasking.task_queue import TaskQueue

# Imports for python variable type hints
from typing import Any, Callable
from apptasking.typing import TaskStatus


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
DEFAULT_LOGGER_NAME = "AppTasking_TaskWrapper"

#
# Global Variables
#


###########################################################################
#
# Task Wrapper
#
###########################################################################
#
# task_wrapper
#
def task_wrapper(
        watchdog_queue: TaskQueue | None = None,
        task_id: str = "",
        start_func: Callable | None = None,
        start_kwargs: dict = {},
        start_event: (
                multiprocessing.synchronize.Event | threading.Event | None
            ) = None,
        stop_event: (
                multiprocessing.synchronize.Event | threading.Event | None
            ) = None,
        logger_name: str = ""
) -> None:
    '''
    Wrapper to run a task, and update result information

    Args:
        watchdog_queue (TaskQueue): Queue to communicate to the watchdog
        task_id (str): ID of the task
        start_func (Callable): Callable to run in the new thread/process
        start_kwargs (dict): Arguments to pass to the start function
        start_event (Event): Event to be set when task is running
        stop_event (Event): Event to be set when task is finished
        logger_name (str): The name of the logger to use.

    Returns:
        None

    Raises:
        AssertionError:
            When watchdog queue is not a TaskQueue
    '''
    assert isinstance(watchdog_queue, TaskQueue), (
        "watchdog_queue must be a TaskQueue"
    )

    # Get the logger
    if isinstance(logger_name, str) and logger_name:
        _logger = get_logger(name=logger_name)

    else:
        _logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
        _logger.setLevel(level="CRITICAL")

    # The task status info
    _info = {
        "id": task_id,
        "status": TaskStatus.RUNNING.value,
        "return_value": None,
        "exception_name": "",
        "exception_desc": "",
        "exception_stack": ""
    }

    # Send the status to the watchdog
    watchdog_queue.put(item=_info)

    # Got here - so let the caller know the task has started
    if isinstance(
        start_event,
        (multiprocessing.synchronize.Event, threading.Event)
    ):
        start_event.set()

    if callable(start_func):
        # Run the start function, capturing any exceptions and the return value
        try:
            _info["return_value"] = start_func(**start_kwargs)
            _info["status"]= TaskStatus.COMPLETED.value
            _logger.debug(f"Task finished OK: {str(start_func)}")

        except Exception:
            _info["status"]= TaskStatus.ERROR.value
            _info["exception_stack"] = traceback.format_exc()
            _logger.debug(f"Task FAILED: {str(start_func)}")
            _logger.debug(_info["exception_stack"])

            _exc_info = sys.exc_info()
            if _exc_info:
                if _exc_info[0]:
                    _info["exception_name"] = str(_exc_info[0].__name__)
                if _exc_info[1]:
                    _info["exception_desc"] = str(_exc_info[1])

    else:
        _info["status"]= TaskStatus.NOT_RUNNABLE.value

    # Send the status to the watchdog
    watchdog_queue.put(item=_info)

    # Set the stop event
    if isinstance(
        stop_event,
        (multiprocessing.synchronize.Event, threading.Event)
    ):
        stop_event.set()


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
