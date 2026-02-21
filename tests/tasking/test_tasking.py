#!/usr/bin/env python3
'''
PyTest - Test of Tasking

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
import time

# Local app modules
from apptasking.tasking import Tasking
from apptasking.typing import TaskStatus

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
EXCEPTION = RuntimeError
EXCEPTION_DESC = "The exception description"

SHORT_LIVED_RETURN = "short lived task return string"


###########################################################################
#
# Functions to run in the tasks
#
###########################################################################
#
# Simple task to end when an event is set
#
def simple_event_target(test_event=None):
    assert test_event
    test_event.clear()
    test_event.wait()


def simple_event_stop(test_event=None):
    assert test_event
    test_event.set()


#
# Task to end by itself
#
def short_lived_event_target():
    return SHORT_LIVED_RETURN


#
# Task to generate an error
#
def error_event_target():
    raise EXCEPTION(EXCEPTION_DESC)
    time.sleep(_sleep_time)


###########################################################################
#
# The tests...
#
###########################################################################
#
# Tasks
#
class Test_Tasks():
    '''
    Test Class - Tasks - Test the tasks

    Attributes:
        None
    '''

    #
    # Start a simple task then stop it
    #
    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_task_simple(self, task_type):
        ''' Run task and stop it '''
        # Create a task manager
        _task_mgr = Tasking(task_type=task_type)
        
        _kwargs = {
            "test_event": _task_mgr.Event()
        }

        # Add a task
        _task = _task_mgr.create(
            name=f"Test Task - Simple ({task_type})",
            start_func=simple_event_target,
            start_kwargs=_kwargs,
            stop_func=simple_event_stop,
            stop_kwargs=_kwargs
        )

        # Start the task
        _task.start()

        # Stop the task
        _task.stop()


    #
    # Check the status of a successful task during it's lifecycle
    #
    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_task_status_complete(self, task_type):
        ''' Run task, checking the status being set correctly '''
        # Create a task manager
        _task_mgr = Tasking(task_type=task_type)
        
        _kwargs = {
            "test_event": _task_mgr.Event()
        }

        # Add a task
        _task = _task_mgr.create(
            name=f"Test Task - Status Complete ({task_type})",
            start_func=simple_event_target,
            start_kwargs=_kwargs,
            stop_func=simple_event_stop,
            stop_kwargs=_kwargs
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()
        assert _task.status == TaskStatus.RUNNING.value

        # Stop the task
        _task.stop()
        assert _task.status == TaskStatus.COMPLETED.value


    #
    # Check the status of a unsuccessful task during it's lifecycle
    #
    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_task_status_error(self, task_type):
        ''' Run task, checking the status being set correctly '''
        # Create a task manager
        _task_mgr = Tasking(task_type=task_type)

        # Add a task
        _task = _task_mgr.create(
            name=f"Test Task - Status Error ({task_type})",
            start_func=error_event_target
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()

        # Allow time for the task to start then fail
        time.sleep(0.5)
        assert _task.status == TaskStatus.ERROR.value

        # Check the results
        assert not _task.return_value
        assert _task.exception_name == str(EXCEPTION.__name__)
        assert _task.exception_desc == EXCEPTION_DESC
        assert str(_task.exception_stack).find(
                f"{EXCEPTION.__name__}: {EXCEPTION_DESC}") >= 0


    #
    # Check the return value from a task
    #
    @pytest.mark.parametrize("task_type", TASK_TYPES)
    def test_task_check_return_value(self, task_type):
        ''' Run a task that ends itself and returns a value '''
        # Create a task manager
        _task_mgr = Tasking(task_type=task_type)

        # Add a task
        _task = _task_mgr.create(
            name=f"Test Task - Check Return Value ({task_type})",
            start_func=short_lived_event_target
        )

        assert _task.status == TaskStatus.NOT_STARTED.value

        # Start the task
        _task.start()
        time.sleep(0.5)

        # What for the task to complete
        while _task.status == TaskStatus.RUNNING.value:
            time.sleep(0.1)

        # Check the results
        assert _task.status == TaskStatus.COMPLETED.value
        assert _task.return_value == SHORT_LIVED_RETURN

        # Remove the task
        _task_mgr.delete(task_id=_task.task_id)


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

