#!/usr/bin/env python3
'''
AppTasking - Tasking Class

Copyright (C) 2025 Jason Piszcyk
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
import multiprocessing
import multiprocessing.synchronize
import threading
import queue
from applogging.logging import get_logger, init_console_logger

# Local app modules
from apptasking.task_wrapper import task_wrapper, get_default_task_info

# Imports for python variable type hints
from typing import Callable
from apptasking.typing import TaskType_Type, ProcessMethod_Type, TaskStatus


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
# DataStoreMem Class Definition
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
            process_method: ProcessMethod_Type = "spawn",
            logger_name: str = "",
            logger_level: str = "CRITICAL"
    ):
        '''
        Initialises the instance.

        Args:
            task_type (str): The type of task ("thread", "process")
                to be created and managed by this instance
            process_method (str): When task_type is "process", specify the
                method to created new processes. Valid values are "spawn",
                "fork", "forkserver".
            logger_name (str): The name of the logger to use.  If empty (or
                not a string) then a logger will be created to log to the
                console
            logger_level (str): If no logger name is provided, the created
                logger will be set to log events at or above this level (default
                = "CRITICAL")

        Returns:
            None

        Raises:
            None
        '''
        assert task_type in TaskType_Type, (
            f"task_type must be one of {TaskType_Type}"
        )
        assert process_method in ProcessMethod_Type, (
            f"process_method must be one of {ProcessMethod_Type}"
        )

        # Private Attributes
        self._task_type = task_type
        self._context = multiprocessing.get_context(method=process_method)

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


    #
    # process_method
    #
    @property
    def process_method(self) -> str:
        ''' The method used when creating new processes '''
        return self._context.get_start_method()


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
            TypeError:
                When task_type is not valid
        '''
        self._logger.debug(f"Creating event")

        if self._task_type == "thread":
            return threading.Event()

        elif self._task_type == "process":
            return multiprocessing.Event()

        else:
            raise TypeError("task_type is invalid")


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
            TypeError:
                When task_type is not valid
        '''
        self._logger.debug(f"Creating lock")

        if self._task_type == "thread":
            return threading.Lock()

        elif self._task_type == "process":
            return multiprocessing.Lock()

        else:
            raise TypeError("task_type is invalid")


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
            TypeError:
                When task_type is not valid
        '''
        self._logger.debug(f"Creating barrier")

        if self._task_type == "thread":
            return threading.Barrier(
                parties=parties,
                action=action,
                timeout=timeout
            )

        elif self._task_type == "process":
            return multiprocessing.Barrier(
                parties=parties,
                action=action,
                timeout=timeout
            )

        else:
            raise TypeError("task_type is invalid")


    #
    # Queue
    #
    def Queue(self) -> multiprocessing.Queue | queue.Queue:
        '''
        Create a Queue suitable for the task_type

        Args:
            None

        Returns:
            Queue: An instance of a Taskqueue

        Raises:
            None
        '''
        self._logger.debug(f"Creating queue")

        if self._task_type == "thread":
            return queue.Queue()

        elif self._task_type == "process":
            return multiprocessing.Queue()

        else:
            raise TypeError("task_type is invalid")


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
            stop_kwargs: dict = {},
            store_results: bool = False,
            start: bool = True,
            watchdog: bool = False,
            restart: bool = True
    ) -> None:
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
            store_results (bool): If True, make the results of the start
                function available upon completion
            start (bool): If True, start the task after creating it
            watchdog (bool): If True, add the task to the watchdog thread
                to keep track of the task (auto restart, etc)
            restart (bool): If task has been added to the watchdog, and
                'restart' is True, an attempt will be made to restart the
                task when it ends or fails.

        Returns:
            Any: The value of the item

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

        # Create event to manage to the task lifecycle
        _start_event = self.Event()
        _stop_event = self.Event()

        # Ensure the events are cleared
        _start_event.clear()
        _stop_event.clear()

        # Create the task info dict
        _info = get_default_task_info()

        # self.__info["status"] = TaskStatus.RUNNING.value

        # self.logger.debug(f"Start: Task Type = {self.__task_type}")

        # Wrap the target functions to gather information
        _kwargs = {
            "start_func": start_func,
            "start_kwargs": start_kwargs,
            "logger_name": self._logger.name,
        }

        if self._task_type == "thread":
            # Start the thread
            _thread = threading.Thread(
                target=task_wrapper,
                kwargs=_kwargs,
                name=name
            )
            _thread.start()
            # self.__thread_id = _thread.native_id

        elif self._task_type == "process":
            _process = self._context.Process(               # type: ignore
                target=task_wrapper,
                kwargs=_kwargs,
                name=name
            )
            _process.start()
            # self.__process_id = _process.pid


            # When the process/thread is started, wait for the event
            # self.__start_event.wait(timeout=TASK_START_TIMEOUT)

        else:
            raise TypeError("task_type is invalid")

        self._logger.debug(
            f"Start: Task Started: {name} (Type={self._task_type})"
        )




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
