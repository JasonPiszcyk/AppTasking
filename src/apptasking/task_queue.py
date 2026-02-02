#!/usr/bin/env python3
'''
Task Queue - Extension of the queue to include additional functionality

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
import enum
import queue
from applogging.logging import get_logger, init_console_logger

# Local app modules
import apptasking.tasking_ipc as tasking_ipc

# import appcore.multitasking.exception as exception

# Imports for python variable type hints
from typing import Any, Callable, get_args
from apptasking.typing import TaskType_Type


###########################################################################
#
# Module Specific Items
#
###########################################################################
#
# Types
#
# The message types
class MessageType(enum.Enum):
    DATA                = "__message_type_data__"
    LISTENER_EXIT       = "__message_type_listener_exit__"
    LISTENER_KEEPALIVE  = "__message_type_listener_keepalive__"

#
# Constants
#
DEFAULT_LOGGER_NAME = "AppTasking_AppQueue"

STOP_WAIT_TIMEOUT: float = 5.0
MAX_KEEPALIVE_INTERVAL = 3600

#
# Global Variables
#


###########################################################################
#
# TaskQueue_Frame Class
#
###########################################################################
class TaskQueue_Frame():
    '''
    Class to describe a Task Queue message frame

    The queue message frame describes the structure of data to be passed
    in the message.

    Attributes:
        message_type (MessageType): The type of message being sent
        data (Any): The data sent via the queue
    '''

    #
    # __init__
    #
    def __init__(
            self,
            message_type: MessageType = MessageType.DATA,
            data: Any = None,
    ):
        '''
        Initializes the instance.

        Args:
            message_type (MessageType): The type of message being sent
            data: The data sent via the queue
            response_queue (TaskQueue): The queue to send the response to
            message_id (str): An ID for the message (UUID will be generated if
                empty)
            session_id (str): The message can be related to other messages
                via this ID
        
        Returns:
            None

        Raises:
            None
        '''
        # Private properties

        # Attributes
        if message_type in MessageType:
            self.message_type: MessageType = message_type
        else:
            self.message_type: MessageType = MessageType.DATA

        self.data = data


###########################################################################
#
# TaskQueue Class Definition
#
###########################################################################
class TaskQueue():
    '''
    Class to describe a TaskQueue.
    
    Extension to a basic queue to include some basic message framing, and 
    a standard listener function to listen for and process messages.

    Attributes:
        listener_running (bool) [ReadOnly]: Indicates if the listener is
            currently running in this process/thread.
    '''

    #
    # __init__
    #
    def __init__(
            self,
            task_type: TaskType_Type = "process",
            logger_name: str = ""
    ):
        '''
        Initialises the instance.

        Args:
            task_type (str): The type of task ("thread", "process")
                to be supported by this Queuing instance. "process" works
                with both threads and process so is safer, but has more
                overhead
            logger_name (str): The name of the logger to use.

        Returns:
            None

        Raises:
            AssertionError
                When task_type is not valid
        '''
        assert task_type in get_args(TaskType_Type), (
            f"task_type must be one of {get_args(TaskType_Type)}"
        )

        # Private Attributes
        self._task_type = task_type
        self._queue = tasking_ipc._create_queue(task_type=task_type)
        self._stop_event = tasking_ipc._create_event(task_type=task_type)
        self._listener_running = False

        # Get the logger
        if isinstance(logger_name, str) and logger_name:
            self._logger = get_logger(name=logger_name)

        else:
            self._logger = init_console_logger(name=DEFAULT_LOGGER_NAME)
            self._logger.setLevel(level="CRITICAL")

        # Attributes
        self._message_handler = None
        self._keepalive_interval = 0


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
        ''' The task type supported by this instance '''
        return self._task_type


    #
    # listener_running
    #
    @property
    def listener_running(self) -> bool:
        ''' Boolean property indicating if the listener is running '''
        return self._listener_running


    ###########################################################################
    #
    # Message processing
    #
    ###########################################################################
    #
    # _put_frame
    #
    def _put_frame(
            self,
            message_type: MessageType = MessageType.DATA,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None
    ):
        '''
        Put a message on the queue with the specified message type

        Args:
            message_type (MessageType): The type of message being sent
            item (Any): The data to be sent
            block (bool): If True block until message is placed on queue. If 
                false, return immediately
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            None

        Raises:
            AssertionError
                When message type is not valid
                When block is not bool
                When timeout is not a positive float, 0 or None
        '''
        self._logger.debug(f"Placing item on queue: f{item}")

        assert message_type in MessageType, "message_type is not valid"
        assert isinstance(block, bool), "block must be of type bool"
        assert isinstance(timeout, float) or timeout is None, (
            "timeout must None or of type float"
        )
        if isinstance(timeout, float):
            assert timeout >= 0, "timeout must be 0, or positive"

        _frame = TaskQueue_Frame(message_type=message_type, data=item)

        # Put a message on the queue
        self._queue.put(_frame, block=block, timeout=timeout)


    #
    # _get_frame
    #
    def _get_frame(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> TaskQueue_Frame:
        '''
        Get a Task Queue message frame from the queue

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            TaskQueue_Frame: The Task Queue message frame sent via the queue

        Raises:
            AssertionError
                When block is not bool
                When timeout is not a positive float, 0 or None
            TypeError
                When the task queue message frame is not valid
            AttributeError
                When the frame message type is invalid
        '''
        self._logger.debug("Getting item from queue")

        assert isinstance(block, bool), "block must be of type bool"
        assert isinstance(timeout, float) or timeout is None, (
            "timeout must None or of type float"
        )
        if isinstance(timeout, float):
            assert timeout >= 0, "timeout must be 0, or positive"

        # Get a message from the queue
        _frame = self._queue.get(block=block, timeout=timeout)

        # Confirm the message is in the correct format
        if not isinstance(_frame, TaskQueue_Frame):
            raise TypeError(
                "Task Queue message format is incorrect"
            )

        # Confirm the frame is a valid type
        if _frame.message_type not in MessageType:
            raise AttributeError("Invalid message type in frame")

        self._logger.debug(f"Got item from queue: Type={_frame.message_type}")
        self._logger.debug(f"Got item from queue: Data={_frame.data}")

        return _frame


    #
    # put
    #
    def put(
            self,
            item: Any = None,
            block: bool = True,
            timeout: float | None = None
    ):
        '''
        Wrapper for _put_type specifying a type of 'DATA'

        Args:
            item (Any): The data to be sent
            block (bool): If True block until message is placed on queue. If 
                false, return immediately
            timeout: Time (in seconds) to wait before returning

        Returns:
            None

        Raises:
            None
        '''
        # Put a message on the queue with a type of 'DATA'
        self._put_frame(
            message_type=MessageType.DATA,
            item=item,
            block=block,
            timeout=timeout
        )


    #
    # get
    #
    def get(
            self,
            block: bool = True,
            timeout: float | None = None
    ) -> Any:
        '''
        Get a message frame from the queue

        Args:
            block (bool): If True block until message received. If false,
                check for message and return
            timeout: Time (in seconds) to wait before returning
        
        Returns:
            Any: item retrieved from the queue

        Raises:
            TypeError
                When the task queue message frame is not valid
            AttributError
                When an invalid message type is received
        '''
        # Get a message from the queue
        _frame = self._get_frame(block=block, timeout=timeout)

        # Confirm the message is in the correct format
        if not isinstance(_frame, TaskQueue_Frame):
            raise TypeError(
                "Task Queue message format is incorrect"
            )

        if _frame.message_type != MessageType.DATA:
            # Ignore anything other than DATA, as they are system messages
            # that should not be handled by this method.
            raise AttributeError(
                "invalid task_queue message received"
            )

        return _frame.data


    ###########################################################################
    #
    # Standard Listener
    #
    ###########################################################################
    #
    # cleanup
    #
    def cleanup(self):
        '''
        Clean up the queue (eg remove all messages)

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug("Cleaning Queue")

        _queue_not_empty = True
        while _queue_not_empty:
            try:
                _ = self._queue.get(block=False)
            except queue.Empty:
                _queue_not_empty = False


    #
    # listener
    #
    def listener(
            self,
            message_handler: Callable | None = None,
            keepalive_interval: int = 0
    ):
        '''
        Listen for messages on the queue and hand off to the message_handler.

        Args:
            message_handler (Callable): Callable to process the received
                message. The message handler should accept 1 parameter:
                    item - The data retrieved from the queue
                No return value is expected from the message handler
            keepalive_interval (int): How often to send KeepAlive messages.
                If 0, set to MAX_KEEPALIVE_INTERVAL
        
        Returns:
            None

        Raises:
            AssertionError
                When message_handler is not a callable
            TypeError
                When the task queue message frame is not valid
            AttributeError
                When the frame message type is invalid
            RuntimeError
                When the queue is not processing messages
        '''
        assert callable(message_handler), "message_handler must be callable"
        assert isinstance(keepalive_interval, int), (
            "keepalive_interval must be an integer"
        )
        assert keepalive_interval >= 0, "keepalive_interval must be >= 0"

        self._logger.debug(f"Starting Listener")

        # If the listener is already running, just return
        if self._listener_running: return

        # Make sure the keepalive doesn't exceed the internal max
        if (
            self._keepalive_interval == 0 or 
            self._keepalive_interval > MAX_KEEPALIVE_INTERVAL
        ):
            self._keepalive_interval = MAX_KEEPALIVE_INTERVAL

        self._listener_running = True
        _timed_out_previous = False
        while self._listener_running:
            _frame = None
            _keepalive_interval_exceeded = False

            try:
                # Only wait for half the keepalive interval
                # If it times out twice in a row, messages are NOT being
                # processed
                _frame = self._get_frame(
                    block=True,
                    timeout=self._keepalive_interval / 2
                )

            except queue.Empty:
                # should be due to keepalive interval
                if _timed_out_previous:
                    _keepalive_interval_exceeded = True
                else:
                    _timed_out_previous = True

            if _keepalive_interval_exceeded:
                raise RuntimeError("message not being processed on queue")

            if _timed_out_previous:
                # Should send a keep alive to make sure the Queue is OK
                # If it fails will raise queue.Full
                self._put_frame(
                    message_type=MessageType.LISTENER_KEEPALIVE,
                    item=MessageType.LISTENER_KEEPALIVE.value,
                    block=False
                )
                continue

            if not isinstance(_frame, TaskQueue_Frame):
                raise TypeError(
                    "Task Queue message format is incorrect"
                )

            # Make sure the message type is valid
            if _frame.message_type not in MessageType:
                raise AttributeError("Invalid message type in frame")

            # A message was received
            _timed_out_previous = False

            # The exit message
            if _frame.message_type == MessageType.LISTENER_EXIT:
                # The listener exit message frame was received
                self._listener_running = False
                continue

            # A keepalive - Ignore it
            if _frame.message_type == MessageType.LISTENER_KEEPALIVE:
                continue

            # It's a data message
            if callable(self._message_handler):
                self._message_handler(_frame.data)


        # Set the stop event
        if self._stop_event: self._stop_event.set()


    #
    # listener_stop
    #
    def listener_stop(self):
        '''
        Stop the listener

        Args:
            None
        
        Returns:
            None

        Raises:
            None
        '''
        self._logger.debug(f"Stopping Listener")
        
        if self._stop_event: self._stop_event.clear()

        # Put an EXIT message on the queue
        self._put_frame(
            message_type=MessageType.LISTENER_EXIT,
            item=MessageType.LISTENER_EXIT.value
        )

        # If the stop_event exists, wait for it
        if self._stop_event:
            self._stop_event.wait(timeout=STOP_WAIT_TIMEOUT)


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
