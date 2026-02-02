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
import uuid

from appdatastore.mem import DataStoreMem
from applogging.logging import get_logger, init_console_logger

# Local app modules
from apptasking.task_queue import TaskQueue

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

JOIN_TIMEOUT = 5.0
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
            interval: float = DEFAULT_CHECK_INTERVAL,
            logger_name: str = ""
    ):
        '''
        Initialises the instance.

        Args:
            interval (float): How often the watchdog (in seconds) wakes up
                and checks tasks
            logger_name (str): The name of the logger to use.

        Returns:
            None

        Raises:
            AssertionError:
                When interval is not a postive number
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
        self._interval = interval

        # Start the thread
        self._watchdog_thread = threading.Thread(
            target=task_wrapper,
            kwargs={},
            name=name
        )
        self._watchdog_thread.start()

        # Attributes


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
    # The watchdog processing
    #
    ###########################################################################
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

        # The message handler for any incoming messages
        def _message_handler(item):
            # If something fails, go to sleep - The join will then fail the test
            _sleep_time = 0.1


        # Check the stop event
        while not self.__stop_event.is_set():
            # Catch everything to keep this running
            try:
                #
                # Tasks to be stopped
                #
                _task_list = list(self.__task_stop_dict.keys())
                for _key in _task_list:
                    # Update telemetry
                    if _key == TELEMETRY_ENTRY:
                        self.__task_stop_dict[_key]['scanned'] = timestamp()
                        continue

                    _task: TaskType = self.__task_stop_dict[_key]
                    self.logger.info(
                        f"Watchdog: Task ({_key}): [id={_task.id}] " +
                        "Stop has been requested"
                    )
                    _task.stop()

                    # Remove the key from all of the dicts
                    if _key in self.__task_start_dict:
                        del self.__task_start_dict[_key]

                    if _key in self.__task_restart_dict:
                        del self.__task_restart_dict[_key]

                    del self.__task_stop_dict[_key]

                #
                # Tasks to be started
                #
                _task_list = list(self.__task_start_dict.keys())
                for _key in _task_list:
                    # Update telemetry
                    if _key == TELEMETRY_ENTRY:
                        self.__task_start_dict[_key]['scanned'] = timestamp()
                        continue

                    _task: TaskType = self.__task_start_dict[_key]
                    self.logger.info(
                        f"Watchdog: Task ({_key}): Start has been requested"
                    )
                    _task.start()

                    # Move the task to the restart dict
                    self.__task_restart_dict[_key] = _task
                    del self.__task_start_dict[_key]

                #
                # Tasks to be watched and restarted if necessary
                #
                _task_list = list(self.__task_restart_dict.keys())
                for _key in _task_list:
                    # Update telemetry
                    if _key == TELEMETRY_ENTRY:
                        self.__task_restart_dict[_key]['scanned'] = timestamp()
                        continue

                    _task: TaskType = self.__task_restart_dict[_key]

                    _restart_task = False
                    if _task.status != TaskStatus.RUNNING.value:
                        _restart_task = True
                        self.logger.warning(
                            f"Watchdog: Task ({_key}: [id={_task.id}] " +
                            f"{_task.name}) not running.  Status: " +
                            f"{_task.status}"
                        )

                    elif not _task.is_alive:
                        _restart_task = True
                        self.logger.warning(
                            f"Watchdog: Task ({_key}: [id={_task.id}] " +
                            f"{_task.name}) not running.  Task not alive"
                        )

                    if _restart_task:
                        _task.cleanup()
                        _task.start()
                        self.logger.info(
                            f"Watchdog: Task ({_key}: {_task.name}) " +
                            "restarted"
                        )

            except:
                self.logger.error("Watchdog has failed", exc_info=True)

            # Pause for the interval - Can be woken up if needed
            if self.__interval_event.wait(timeout=interval):
                # Got woken up - Reset the event
                self.__interval_event.clear()


        # Set all tasks to be stopped
        self.logger.debug("Stopping registered tasks")

        _task_list = list(self.__task_start_dict.keys())
        for _key in _task_list:
            # Update telemetry
            if _key == TELEMETRY_ENTRY:
                self.__task_start_dict[_key]['scanned'] = timestamp()
                continue

            _task: TaskType = self.__task_start_dict[_key]
            self.logger.debug(f"Setting stop (start): {_task.name}")
            self.__task_stop_dict[_key] = _task
            del self.__task_start_dict[_key]

        _task_list = list(self.__task_restart_dict.keys())
        for _key in _task_list:
            # Update telemetry
            if _key == TELEMETRY_ENTRY:
                self.__task_restart_dict[_key]['scanned'] = timestamp()
                continue

            _task: TaskType = self.__task_restart_dict[_key]
            self.logger.debug(f"Setting stop (restart): {_task.name}")
            self.__task_stop_dict[_key] = _task
            del self.__task_restart_dict[_key]

        _task_list = list(self.__task_stop_dict.keys())
        for _key in _task_list:
            # Update telemetry
            if _key == TELEMETRY_ENTRY:
                self.__task_stop_dict[_key]['scanned'] = timestamp()
                continue

            _task: TaskType = self.__task_stop_dict[_key]
            self.logger.debug(f"Stopping: {_task.name}")
            _task.stop()
            del self.__task_stop_dict[_key]

        # Indicate the shutdown is complete
        self.logger.debug("Shutdown done")
        self.__shutdown_event.set()

        # Reset the events
        self.__stop_event.clear()
        self.__interval_event.clear()
        self.logger.debug("Watchdog: Ending")


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
        self.logger.debug("Request to stop Watchdog")

        # Set the events to exit the loop
        self.__interval_event.set()
        self.__stop_event.set()

        # Let the watchdog stop
        self.__shutdown_event.wait(timeout=WATCHDOG_SHUTDOWN_TIMEOUT)

        # Join the watchdog thread to clean it up
        for _thread in enumerate_threads():
            if _thread.name == self.task_id:
                self.logger.debug("Found Thread - Joining")
                _thread.join(timeout=WATCHDOG_JOIN_TIMEOUT)

        self.logger.debug("Request to stop Watchdog completed")


    ###########################################################################
    #
    # Add/Remove tasks to watch
    #
    ###########################################################################
    #
    # register
    #
    def register(
            self,
            task: TaskType | None = None,
            label: str = ""
    ) -> str:
        '''
        Register a task with the watchdog

        Args:
            task (Task): An AppCore task to be watched
            label (str): A label for the task within the watchdog.  If empty,
                a UUID will be allocated.

        Returns:
            str: The label of the task in the watchdog

        Raises:
            AssertionError:
                when a task is not provied
        '''
        assert isinstance(task, TaskType), \
            "A task is required to register with the watchdog"
        assert isinstance(label, str), "Label must be a string"

        if self.__thread_only:
            assert task.type == "thread", \
                "Watchdog configured to only watch thread type tasks"

        # If the label is empty, generate a uuid as a label
        if not label: label = str(uuid.uuid4())

        self.logger.debug(f"Registering Task: {label}")

        # Add the entry to the start task dict
        self.__task_start_dict[label] = task

        # Don't wait for the watchdog interval - Do this immediately
        self.__interval_event.set()

        return label


    #
    # deregister
    #
    def deregister(
            self,
            label: str = ""
    ):
        '''
        Register a task with the watchdog

        Args:
            label (str): The label for the task within the watchdog.

        Returns:
            None

        Raises:
            None
        '''
        assert isinstance(label, str), "Label must be a string"

        self.logger.debug(f"Deregistering Task: {label}")

        # Set the task to be stopped
        if label in self.__task_start_dict:
            self.__task_stop_dict[label] = self.__task_start_dict[label]

        elif label in self.__task_restart_dict:
            self.__task_stop_dict[label] = self.__task_restart_dict[label]

        self.__interval_event.set()


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
