#!/usr/bin/env python3
'''
PyTest - Test of Task Queue Function

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
# Shared variables, constants, etc
from tests.constants import *

# System Modules
import pytest
import multiprocessing
import threading
import time

# Local app modules
from apptasking.task_queue import TaskQueue

# Imports for python variable type hints
from typing import Any, Final


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
TASK_WAIT = 5.0

#
# Global Variables
#


###########################################################################
#
# Functions to run in the thread/process
#
###########################################################################
#
# Simple task to get from a queue
#
def simple_get_queue(
        q: TaskQueue | None = None,
        data_value: Any = None,
        data_type: type = str
):
    # If something fails, go to sleep - The join will then fail the test
    _sleep_time = 0.1

    if not isinstance(q, TaskQueue):
        _sleep_time = TASK_WAIT + 1.0
    else:
        _item = q.get()
        if not isinstance(_item, data_type): _sleep_time = TASK_WAIT + 1.0
        if not _item == data_value: _sleep_time = TASK_WAIT + 1.0

    time.sleep(_sleep_time)


#
# Simple task to put in a queue
#
def simple_put_queue(
        q: TaskQueue | None = None,
        data_value: Any = None,
):
    # If something fails, go to sleep - The join will then fail the test
    _sleep_time = 0.1

    if not isinstance(q, TaskQueue):
        _sleep_time = TASK_WAIT + 1.0
    else:
        q.put(data_value)

    time.sleep(_sleep_time)



#
# Simple task to start the listener in a task
#
def simple_queue_listener(q: TaskQueue | None = None):
    # If something fails, go to sleep - The join will then fail the test
    _sleep_time = 0.1

    if not isinstance(q, TaskQueue):
        _sleep_time = TASK_WAIT + 1.0
    else:
        q.listener(message_handler=message_handler)

    time.sleep(_sleep_time)


#
# Message handler that raises an exception if the message isn't correct
#
def message_handler(item):
    # If something fails, go to sleep - The join will then fail the test
    _sleep_time = 0.1

    # The test sends of DATA_DICT
    if not isinstance(item, dict):
        _sleep_time = TASK_WAIT + 1.0
    else:
        if not "value" in item:
            _sleep_time = TASK_WAIT + 1.0
        else:
            if not "value" in DATA_DICT:
                _sleep_time = TASK_WAIT + 1.0
            else:
                if not item["value"] == DATA_DICT["value"]:
                    _sleep_time = TASK_WAIT + 1.0

    time.sleep(_sleep_time)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Task Queue - Process
#
class Test_TaskQueue_Process():
    '''
    Test Class - TaskQueue - With type of "process"

    Attributes:
        None
    '''
    _task_type: Final = "process"

    #
    # Basic Tests - put then get
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_basic(self, name):
        '''
        Basic tests

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        _q = TaskQueue(task_type=self._task_type)

        _q.put(DATA_SET[name]["value"])

        _item = _q.get()
        assert isinstance(_item, DATA_SET[name]["type"])
        assert _item == DATA_SET[name]["value"]


    #
    # Separate thread - Read from Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_read_q_from_thread(self, name):
        '''
        Read the Q in a separate thread

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_SET[name]["value"])

        # Create a thread to get the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"],
            "data_type": DATA_SET[name]["type"]
        }

        _task = threading.Thread(
            name = f"Task Q - Get Thread",
            target = simple_get_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)


    #
    # Separate process - Write to Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_write_q_from_thread(self, name):
        '''
        Write to the Q in a separate thread

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Create a process to put the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"]
        }

        _task = threading.Thread(
            name = f"Task Q - Put Thread",
            target = simple_put_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)

        # Get the value and check it
        _item = _q.get()
        assert isinstance(_item, DATA_SET[name]["type"])
        assert _item == DATA_SET[name]["value"]


    #
    # Separate process - Read from Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_read_q_from_process(self, name):
        '''
        Read the Q in a separate process

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_SET[name]["value"])

        # Create a process to get the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"],
            "data_type": DATA_SET[name]["type"]
        }

        _task = multiprocessing.Process(
            name = f"Task Q - Get Process",
            target = simple_get_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)


    #
    # Separate process - Write to Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_write_q_from_process(self, name):
        '''
        Write to the Q in a separate process

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Create a process to put the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"]
        }

        _task = multiprocessing.Process(
            name = f"Task Q - Put Process",
            target = simple_put_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)

        # Get the value and check it
        _item = _q.get()
        assert isinstance(_item, DATA_SET[name]["type"])
        assert _item == DATA_SET[name]["value"]


    #
    # Separate process - Listener
    #
    def test_listener_in_process(self):
        '''
        Run a listener in a separate process

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_DICT)

        # Create a process to run the listener
        _kwargs = { "q": _q }

        _task = multiprocessing.Process(
            name = f"Task Q - Run Listener Process",
            target = simple_queue_listener,
            kwargs = _kwargs
        )

        # Start the task
        _task.start()

        # Finish the listener
        _q.listener_stop()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)


#
# Task Queue - Thread
#
class Test_TaskQueue_Thread():
    '''
    Test Class - TaskQueue - With type of "thread"

    Attributes:
        None
    '''
    _task_type: Final = "thread"

    #
    # Basic Tests - put then get
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_basic(self, name):
        '''
        Basic tests

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        _q = TaskQueue(task_type=self._task_type)

        _q.put(DATA_SET[name]["value"])

        _item = _q.get()
        assert isinstance(_item, DATA_SET[name]["type"])
        assert _item == DATA_SET[name]["value"]


    #
    # Separate thread - Read from Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_read_q_from_thread(self, name):
        '''
        Read the Q in a separate thread

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_SET[name]["value"])

        # Create a thread to get the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"],
            "data_type": DATA_SET[name]["type"]
        }

        _task = threading.Thread(
            name = f"Task Q - Get Thread",
            target = simple_get_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)


    #
    # Separate process - Write to Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_write_q_from_thread(self, name):
        '''
        Write to the Q in a separate thread

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Create a process to put the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"]
        }

        _task = threading.Thread(
            name = f"Task Q - Put Thread",
            target = simple_put_queue,
            kwargs = _kwargs,
        )

        # Start the task
        _task.start()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)

        # Get the value and check it
        _item = _q.get()
        assert isinstance(_item, DATA_SET[name]["type"])
        assert _item == DATA_SET[name]["value"]


    #
    # Separate process - Read from Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_read_q_from_process(self, name):
        '''
        Read the Q in a separate process

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_SET[name]["value"])

        # Create a process to get the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"],
            "data_type": DATA_SET[name]["type"]
        }

        _task = multiprocessing.Process(
            name = f"Task Q - Get Process",
            target = simple_get_queue,
            kwargs = _kwargs,
        )

        # Starting the task fails due to the thread style queue
        with pytest.raises(TypeError, match="cannot pickle"):
            _task.start()


    #
    # Separate process - Write to Q
    #
    @pytest.mark.parametrize("name", DATA_SET)
    def test_write_q_from_process(self, name):
        '''
        Write to the Q in a separate process

        Args:
            name: The name of the data set being tested

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        assert name in DATA_SET
        assert "value" in DATA_SET[name]
        assert "type" in DATA_SET[name]

        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Create a process to put the value
        _kwargs = {
            "q": _q,
            "data_value": DATA_SET[name]["value"]
        }

        _task = multiprocessing.Process(
            name = f"Task Q - Put Process",
            target = simple_put_queue,
            kwargs = _kwargs,
        )

        # Starting the task fails due to the thread style queue
        with pytest.raises(TypeError, match="cannot pickle"):
            _task.start()


    #
    # Separate thread - Listener
    #
    def test_listener_in_thread(self):
        '''
        Run a listener in a separate thread

        Args:
            None

        Returns:
            None

        Raises:
            AssertionError:
                when test fails
        '''
        # Create the Q
        _q = TaskQueue(task_type=self._task_type)

        # Put data on the Q
        _q.put(DATA_DICT)

        # Create a thread to run the listener
        _kwargs = { "q": _q }

        _task = threading.Thread(
            name = f"Task Q - Run Listener Thread",
            target = simple_queue_listener,
            kwargs = _kwargs
        )

        # Start the task
        _task.start()

        # Finish the listener
        _q.listener_stop()

        # Wait for the task to finish
        _task.join(timeout=TASK_WAIT)


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

