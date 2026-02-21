#!/usr/bin/env python3
'''
Watchdog - Track Tasks

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

from appdatastore.mem import DataStoreMem
from applogging.logging import get_logger, init_console_logger
from appcore.helpers import timestamp
import queue

# Local app modules
from apptasking.task_queue import (
    TaskQueue,
    TaskQueue_Frame,
    MessageType,
    MAX_KEEPALIVE_INTERVAL
)
from apptasking.task_task import TaskTask
import apptasking.tasking_ipc as tasking_ipc

# Imports for python variable type hints
# from typing import Any


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
DEFAULT_LOGGER_NAME = "AppTasking_Watchdog"
DEFAULT_CHECK_INTERVAL = 30.0

DS_PREFIX = "AppTasking.Watchdog."

SHUTDOWN_TIMEOUT = 5.0

#
# Global Variables
#


###########################################################################
#
# Watchdog Class Definition
#
###########################################################################
class Watchdog():
    '''
    Class to describe watchdog.

    The watchdog tracks created tasks and associated resources

    Attributes:
        queue (TaskQueue) [ReadOnly]: The queue to communicate with the
            Watchdog
    '''

    #
    # __init__
    #
    def __init__(
            self,
            name: str = "watchdog",
            interval: float = DEFAULT_CHECK_INTERVAL,
            logger_name: str = ""
    ):
        '''
        Initialises the instance.

        Args:
            name (str): Name for the watchdog thread
            interval (float): How often the watchdog (in seconds) wakes up
                and checks tasks
            logger_name (str): The name of the logger to use.

        Returns:
            None

        Raises:
            AssertionError:
                When interval is not a positive number
        '''
        assert isinstance(interval, float), "interval must be a number"
        assert interval > 0, "interval must be positive"

        # Get the logger
        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level="CRITICAL")

        # Private Attributes
        self._memds = DataStoreMem(security="low")
        self._queue = TaskQueue(task_type="process")

        if interval < 1:
            self._interval = 1

        elif interval > MAX_KEEPALIVE_INTERVAL:
            self._interval = MAX_KEEPALIVE_INTERVAL

        else:
            self._interval = interval

        # Start the thread
        self._watchdog_thread = threading.Thread(
            target=self.loop,
            kwargs={},
            name=name
        )
        self._watchdog_thread.start()

        # Attributes
        self._task_dict = {}
        self._task_dict_lock = tasking_ipc._create_lock(task_type="thread")


    #
    # __del__
    #
    def __del__(self):
        '''
        Called when instance is destroyed

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self.cleanup(nowait=True)


    ###########################################################################
    #
    # Properties
    #
    ###########################################################################
    #
    # queue
    #
    @property
    def queue(self) -> TaskQueue:
        ''' The queue to communicate to the watchdog '''
        return self._queue


    ###########################################################################
    #
    # Cleanup
    #
    ###########################################################################
    #
    # cleanup
    #
    def cleanup(self, nowait: bool = False):
        '''
        Perform any shutdown of the watchdog

        Args:
            nowait (bool): If true, just cleanup without waiting for joins

        Returns:
            None

        Raises:
            None
        '''
        # Clean up the watchdog thread
        if isinstance(self._watchdog_thread, threading.Thread):
            # Stop the watchdog loop
            self.loop_stop()

        # Ensure stop is sent to all tasks
        _task_list = list(self._task_dict.values())
        for _task in _task_list:
            _task.stop(join_task=not nowait)


    ###########################################################################
    #
    # The watchdog processing
    #
    ###########################################################################
    #
    # maintenance
    #
    def maintenance(self):
        '''
        The watchdog maintenance

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        # Restart any task that need to be restarted
        for _task in self._task_dict.values():
            if not _task.restart: continue

            # Is the task active?
            if not _task.is_alive:
                _task.start()


    #
    # loop
    #
    def loop(self):
        '''
        The watchdog processing loop

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug("Watchdog: Starting")

        _running = True
        _keepalive_required_by = timestamp(offset=MAX_KEEPALIVE_INTERVAL // 2)
        _timed_out_previous_keepalive = False
        _keepalive_interval_exceeded = False
        
        while _running:
            _frame = None
            _msg_received = False
            _process_keepalive = False

            try:
                # Wait for a message or the interval
                _frame = self._queue.get_frame(
                    block=True,
                    timeout=self._interval
                )
                _msg_received = True

            except queue.Empty:
                # Check if timestamp received within timeframe
                if _keepalive_required_by < timestamp():

                    # Have not received a keepalive within the timeframe
                    if _timed_out_previous_keepalive:
                        _keepalive_interval_exceeded = True
                    else:
                        # Need to perform keepalive processing
                        _process_keepalive = True
                        _timed_out_previous_keepalive = True

            if _keepalive_interval_exceeded:
                raise RuntimeError(
                    "messages not being processed on watchdog queue"
                )

            if _process_keepalive:
                # Should send a keep alive to make sure the Queue is OK
                # If it fails will raise queue.Full
                self._queue.put_keepalive()

            if _msg_received:
                if not isinstance(_frame, TaskQueue_Frame):
                    raise TypeError(
                        "Task Queue message format is incorrect"
                    )

                # Make sure the message type is valid
                if _frame.message_type not in MessageType:
                    raise AttributeError("Invalid message type in frame")

                # The exit message
                if _frame.message_type == MessageType.LISTENER_EXIT:
                    # The listener exit message frame was received
                    _running = False
                    continue

                # A message was received - reset the keepalive info
                _timed_out_previous_keepalive = False
                _keepalive_required_by = timestamp(
                    offset=MAX_KEEPALIVE_INTERVAL // 2
                )

                # Ignore 
                if _frame.message_type == MessageType.DATA:
                    # It's a data message
                    _info = _frame.data

                    # Find the task and update it
                    _task = None
                    if "task_id" in _info:
                        if _info["task_id"] in self._task_dict:
                            _task = self._task_dict[_info["task_id"]]

                    if isinstance(_task, TaskTask):
                        if "status" in _info: self.status = _info["status"]
                        if "return_value" in _info:
                            self.return_value = _info["return_value"]
                        if "exception_name" in _info:
                            self.exception_name = _info["exception_name"]
                        if "exception_desc" in _info:
                            self.exception_desc = _info["exception_desc"]
                        if "exception_stack" in _info:
                            self.exception_stack = _info["exception_stack"]

            # Perform the watchdog maintenance tasks
            self.maintenance()


    #
    # loop_stop
    #
    def loop_stop(self):
        '''
        Stop the watchdog processing loop

        Args:
            None

        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug("Request to stop Watchdog")

        # Send the quit message
        self._queue.put_quit()

        # Join the watchdog thread to clean it up
        self._watchdog_thread.join(timeout=SHUTDOWN_TIMEOUT)

        self._logger.debug("Request to stop Watchdog completed")


    ###########################################################################
    #
    # The watchdog task list
    #
    ###########################################################################
    #
    # add_task
    #
    def add_task(self, task: TaskTask | None = None):
        '''
        Add a task to the watchdog list

        Args:
            task (TaskTask): The task to be added

        Returns:
            None

        Raises:
            AssertionError
                When task is not valid
        '''
        assert isinstance(task, TaskTask), "task must be of type TaskTask"

        self._task_dict_lock.acquire()
        self._task_dict[task.task_id] = task
        self._task_dict_lock.release()


    #
    # remove_task
    #
    def remove_task(self,
            task_id: str = "",
            stop: bool = True,
            join_task: bool = True
    ):
        '''
        Remove a task from the watchdog list

        Args:
            task_id (str): ID of the task to be removed
            stop (bool): If true, attempt to stop the task before removing
            join_task: If True, join the task after running completion func

        Returns:
            None

        Raises:
            AssertionError
                When task is cannot be found
        '''
        assert isinstance(task_id, str), "task_id must be a string"

        self._task_dict_lock.acquire()

        _task = None

        # Delete the task from the dict
        if "task_id" in self._task_dict:
            _task = self._task_dict[task_id]
            del self._task_dict[task_id]

        self._task_dict_lock.release()

        if stop:
            if isinstance(_task, TaskTask):
                _task.stop(join_task=join_task)


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
