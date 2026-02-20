#!/usr/bin/env python3
'''
AppTasking - Tasking Class

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
from applogging.logging import get_logger, init_console_logger

# Local app modules

import apptasking.tasking_ipc as tasking_ipc
from task_task import TaskTask

# Imports for python variable type hints
from typing import Callable, get_args, cast
from apptasking.typing import TaskType_Type


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
DEFAULT_LOGGER_NAME = "AppTasking"

#
# Global Variables
#


###########################################################################
#
# Tasking Class Definition
#
###########################################################################
class Tasking():
    '''
    Class to manage tasking

    Attributes:
        task_type (str) [ReadOnly]: The type of task ("thread", "process")
            created and managed by this instance
    '''
    #
    # __init__
    #
    def __init__(
            self,
            task_type: TaskType_Type = "thread",
            logger_name: str = "",
            logger_level: str = "CRITICAL"
    ):
        '''
        Initialises the instance.

        Args:
            task_type (str): The type of task ("thread", "process")
                to be created and managed by this instance
            logger_name (str): The name of the logger to use.  If empty (or
                not a string) then a logger will be created to log to the
                console
            logger_level (str): If no logger name is provided, the created
                logger will be set to log events at or above this level (default
                = "CRITICAL")

        Returns:
            None

        Raises:
            AssertionError:
                When task_type is not valid
        '''
        assert task_type in get_args(TaskType_Type), (
            f"task_type must be one of {get_args(TaskType_Type)}"
        )

        # Private Attributes
        self._task_type = task_type

        # Configure Logging
        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level=logger_level)


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # task_type
    #
    @property
    def task_type(self) -> str:
        ''' The task type managed by this instance '''
        return self._task_type


    ###########################################################################
    #
    # Inter Process/Thread Communications
    #
    ###########################################################################
    #
    # Event
    #
    def Event(self) -> multiprocessing.synchronize.Event | threading.Event:
        '''
        Create an event suitable for the task_type

        Args:
            None

        Returns:
            Event: An event

        Raises:
            None
        '''
        self._logger.debug(f"Creating event")
        return tasking_ipc._create_event(task_type=self._task_type)


    #
    # Lock
    #
    def Lock(self) -> multiprocessing.synchronize.Lock | threading.Lock:
        '''
        Create a Lock suitable for the task_type

        Args:
            None

        Returns:
            Lock: A lock

        Raises:
            None
        '''
        self._logger.debug(f"Creating lock")
        return tasking_ipc._create_lock(task_type=self._task_type)


    #
    # Barrier
    #
    def Barrier(
            self,
            parties: int = 2,
            action: Callable | None = None,
            timeout: float = 5.0
    ) -> multiprocessing.synchronize.Barrier | threading.Barrier:
        '''
        Create a Barrier suitable for the task_type

        Args:
            parties (int): Number of parties required to wait before the
                barrier is lifted
            action (Callable): Function to be executed (by one of the
                waiting parties) when the barrier is lifted
            timeout (float): Time to wait for the barrier to be lifted

        Returns:
            Barrier: A Barrier

        Raises:
            None
        '''
        self._logger.debug(f"Creating barrier")
        return tasking_ipc._create_barrier(
            task_type=self._task_type,
            parties=parties,
            action=action,
            timeout=timeout
        )


    #
    # Queue
    #
    def Queue(self) -> multiprocessing.Queue | queue.Queue:
        '''
        Create a standard FIFO Queue suitable for the task_type

        Args:
            None

        Returns:
            Queue: An instance of a Taskqueue

        Raises:
            None
        '''
        self._logger.debug(f"Creating queue")
        return tasking_ipc._create_queue(task_type=self._task_type)


    ###########################################################################
    #
    # Task Management
    #
    ###########################################################################
    #
    # create
    #
    def create(
            self,
            name: str = "",
            start_func: Callable | None = None,
            start_kwargs: dict = {},
            stop_func: Callable | None = None,
            stop_kwargs: dict = {}
    ) -> TaskTask:
        '''
        Create a new task

        Args:
            name (str): An identifier for the task.  If not set a random
                name will be provided.
            start_func (Callable): Callable to run in the new thread/process
            start_kwargs (dict): Arguments to pass to the start function
            stop_func (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function

        Returns:
            TaskTask - The task instance

        Raises:
            AssertionError:
                When start_func is not callable
                When start_kwargs is not a dict
                When stop_func is not callable
                When stop_kwargs is not a dict
            TypeError:
                When task_type is not valid
        '''
        assert callable(start_func), "start_func must be a callable"
        assert isinstance(start_kwargs, dict), "start_kwargs must be a dict"

        assert callable(stop_func) or stop_func is None, (
            "stop_func must be a callable, or None"
        )
        assert isinstance(stop_kwargs, dict), "stop_kwargs must be a dict"

        self._logger.debug(
            f"Create task: {name} (Type={self._task_type})"
        )

        _task = TaskTask(
            task_type=cast(TaskType_Type, self._task_type),
            name = name,
            start_func = start_func,
            start_kwargs = start_kwargs,
            stop_func = stop_func,
            stop_kwargs = stop_kwargs,
            logger_name=self._logger.name
        )

        # Add to the watchdog
        # self._watchdog

        return _task


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
