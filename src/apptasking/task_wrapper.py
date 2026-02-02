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
# from appcore.typing import TaskStatus
# from appcore.appcore_base import AppCoreModuleBase

# Imports for python variable type hints
from typing import Any, Callable
from apptasking.typing import TaskStatus

# from threading import Event as EventType
# from logging import Handler as HandlerType
# from appcore.typing import LoggingLevel


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
# Helper Functions
#
###########################################################################
#
# get_default_task_info
#
def get_default_task_info() -> dict:
    '''
    Return a dict with the default task information

    Args:
        None

    Returns:
        dict: The default task information

    Raises:
        None
    '''
    return {
        "status": TaskStatus.NOT_STARTED.value,
        "return_value": None,
        "exception_name": "",
        "exception_desc": "",
        "exception_stack": ""
    }


###########################################################################
#
# Task Wrapper
#
###########################################################################
#
# task_wrapper
#
def task_wrapper(
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
    Wrapper to run a task, and store result information

    Args:
        start_func (Callable): Callable to run in the new thread/process
        start_kwargs (dict): Arguments to pass to the start function
        logger_name (str): The name of the logger to use.

    Returns:
        None

    Raises:
        None
    '''
    # Get the logger
    if isinstance(logger_name, str) and logger_name:
        _logger = get_logger(name=logger_name)

    else:
        _logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
        _logger.setLevel(level="CRITICAL")

    # Got here - so let the caller know the task has started
    if isinstance(
        start_event,
        (multiprocessing.synchronize.Event, threading.Event)
    ):
        start_event.set()

    _info = get_default_task_info()

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
