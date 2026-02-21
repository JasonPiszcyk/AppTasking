#!/usr/bin/env python3
'''
Task Task - Wrapper for the task to provide management functionality

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
import threading
import multiprocessing
import multiprocessing.context
import uuid

# System Modules
from applogging.logging import get_logger, init_console_logger

# Local app modules
from apptasking.task_queue import TaskQueue
from apptasking.task_wrapper import task_wrapper
import apptasking.tasking_ipc as tasking_ipc

# Imports for python variable type hints
from typing import Callable, get_args
from apptasking.typing import TaskType_Type, TaskStatus


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
DEFAULT_LOGGER_NAME = "AppTasking_Task"

TASK_START_TIMEOUT = 5.0
TASK_STOP_TIMEOUT = 5.0

#
# Global Variables
#


###########################################################################
#
# TaskTask Class Definition
#
###########################################################################
class TaskTask():
    '''
    Class to describe a Task.
    
    Encapsulation of the task to provide start/stop, etc

    Attributes:
        task_id (str) [ReadOnly]: ID of the task
        task_type (str) [ReadOnly]: The type of task ("thread", "process")
        is_alive (bool) [ReadOnly]: True if the task is alive, false otherwise
        restart (bool): If True restart the task, if it exits
        status (TaskStatus): Status of the task
        return_value (Any): Value return from the task
        exception_name (str): If error occurred, contains name
        exception_desc (str): If error occurred, contains description
        exception_stack (str): If error occurred, contains stack
    '''

    #
    # __init__
    #
    def __init__(
            self,
            task_type: TaskType_Type = "process",
            watchdog_queue: TaskQueue | None = None,
            name: str = "",
            start_func: Callable | None = None,
            start_kwargs: dict = {},
            stop_func: Callable | None = None,
            stop_kwargs: dict = {},
            restart: bool = False,
            logger_name: str = ""
    ):
        '''
        Initialises the instance.

        Args:
            task_type (TaskType_Type): The type of task ("thread", "process")
                to be supported by this Task instance.
            watchdog_queue (TaskQueue): Queue to communicate to watchdog
            name (str): An identifier for the task.  If not set a random
                name will be provided.
            start_func (Callable): Callable to run in the new thread/process
            start_kwargs (dict): Arguments to pass to the start function
            stop_func (Callable): Function to run to stop the
                thread/process
            stop_kwargs (dict): Arguments to pass the stop function
            restart (bool): If True restart the task, if it exits
            logger_name (str): The name of the logger to use.

        Returns:
            None

        Raises:
            AssertionError
                When task_type is not valid
                When watchdog queue is not a TaskQueue
        '''
        assert task_type in get_args(TaskType_Type), (
            f"task_type must be one of {get_args(TaskType_Type)}"
        )

        assert isinstance(watchdog_queue, TaskQueue), (
            "watchdog_queue must be a TaskQueue"
        )

        # Private Attributes
        self._task_id = str(uuid.uuid4())
        self._task_type = task_type
        self._watchdog_queue = watchdog_queue
        self._name = name or self._task_id
        self._thread: threading.Thread | None = None
        self._process: multiprocessing.context.SpawnProcess | None = None
        self._start_func = start_func
        self._start_kwargs = start_kwargs
        self._stop_func = stop_func
        self._stop_kwargs = stop_kwargs

        # Create events to manage to the task lifecycle
        self._start_event = tasking_ipc._create_event(task_type=task_type)
        self._stop_event = tasking_ipc._create_event(task_type=task_type)

        # Ensure the events are cleared (should be by default)
        self._start_event.clear()
        self._stop_event.clear()

        # Get the logger
        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level="CRITICAL")

        # Attributes
        self.restart = restart
        self.status = TaskStatus.NOT_STARTED.value
        self.return_value = None
        self.exception_name = ""
        self.exception_desc = ""
        self.exception_stack = ""


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # task_id
    #
    @property
    def task_id(self) -> str:
        ''' The task id '''
        return self._task_id


    #
    # task_type
    #
    @property
    def task_type(self) -> str:
        ''' The task type supported by this instance '''
        return self._task_type


    #
    # is_alive
    #
    @property
    def is_alive(self) -> bool:
        ''' Return if the task is alive '''
        if self._task_type == "thread":
            if isinstance(self._thread, threading.Thread):
                return self._thread.is_alive()

        elif self._task_type == "process":
            if isinstance(
                    self._process,
                    multiprocessing.context.SpawnProcess
            ):
                return self._process.is_alive()

        return False


    ###########################################################################
    #
    # Task Start/Stop
    #
    ###########################################################################
    #
    # start
    #
    def start(self):
        '''
        Start the task

        Args:
            None
        
        Returns:
            None

        Raises:
            TypeError:
                When the task type is invalid
        '''
        self._logger.debug(f"Starting task: f{self._name}")

        # Wrap the target functions to gather information
        _kwargs = {
            "watchdog_queue": self._watchdog_queue,
            "task_id": self._task_id,
            "start_func": self._start_func,
            "start_kwargs": self._start_kwargs,
            "start_event": self._start_event,
            "stop_event": self._stop_event,
            "logger_name": self._logger.name,
        }

        if self._task_type == "thread":
            # Start the thread
            self._thread = threading.Thread(
                target=task_wrapper,
                kwargs=_kwargs,
                name=self._name
            )
            self._thread.start()

        elif self._task_type == "process":
            _context = multiprocessing.get_context(method="spawn")
            self._process = _context.Process(
                target=task_wrapper,
                kwargs=_kwargs,
                name=self._name
            )
            self._process.start()

        else:
            raise TypeError("task_type is invalid")

        # Wait for the event to signify the process/thread is started
        self._start_event.wait(timeout=TASK_START_TIMEOUT)

        self._logger.debug(
            f"Start: Task Started: {self._name} (Type={self._task_type})"
        )


    #
    # stop
    #
    def stop(self, join_task: bool = True):
        '''
        Stop the task

        Args:
            join_task: If True, join the task after running completion func
        
        Returns:
            None

        Raises:
            TypeError:
                When the task type is invalid
        '''
        self._logger.debug(f"Stopping task: f{self._name}")

        # Call the stop function
        if callable(self._stop_func):
            self._stop_func(**self._stop_kwargs)

        if join_task:
            if self._task_type == "thread":
                if isinstance(self._thread, threading.Thread):
                    self._thread.join(TASK_STOP_TIMEOUT)
                else:
                    self._logger.debug(f"Unable to find thread info")

                self._thread = None

            elif self._task_type == "process":
                if isinstance(
                        self._process,
                        multiprocessing.context.SpawnProcess
                ):
                    self._process.join(TASK_STOP_TIMEOUT)
                else:
                    self._logger.debug(f"Unable to find process info")

                self._process = None

            else:
                raise TypeError("task_type is invalid")

        self._logger.debug(f"Task stopped: f{self._name}")


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
