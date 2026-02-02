# AppTasking
Copyright (c) 2026 Jason Piszcyk

Applications Components - Tasking

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appnetcomms.svg)](https://pypi.org/project/appnetcomms/)
[![Build Status](https://github.com/JasonPiszcyk/AppnetComms/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppNetComms/actions)
 -->

## Overview

**AppTasking** provides an interface to multithreading and multiprocessing, building on top of the standard python libraries.

## Features

**AppTasking** consists of a number of sub-modules, being:
- [Tasking](#tasking-usage)
  - A generalised Task interface proving multiprocessing via Processes and Threads
    - Task Lifecycle management including starting, stopping and watchdog processing to ensure task state
- [Task Queueing](#queueing-usage)
  - Extension to a FIFO Queue - Can be created for use with processes and thread, or threads only.
  - Implements basic message framing to allow for different internal message types
  - Keepalives implemented to ensure Queues can remain usuable over extended periods of time
  - Implements a standard listener


## Installation

Module has not been published to PyPi yet.  Install via:
```bash
pip install "appnetcomms @ git+https://github.com/JasonPiszcyk/AppTasking"
```

## Requirements

Python >= 3.8

> [!NOTE]
> The module has been tested against Python 3.8 and 3.14.


## Dependencies

- pytest
- "crypto_tools @ git+https://github.com/JasonPiszcyk/CryptoTools"


## Usage

### <a id="tasking-usage"></a>Tasking

#### *class* AppTasking.**Tasking**(*task_type="thread", logger_name="", logger_level="CRITICAL"*)

| Argument | Description |
| - | - |
| **task_type** (str) | The type of tasks ("thread", "process") to be created and managed by this instance. Default = "thread" |
| **logger_name** (str) | The name of the logger to use.  If empty (or not a string) then a logger will be created to log to the console |
| **logger_level** (str) | If no logger name is provided, the created logger will be set to log events at or above this level (default = "CRITICAL") |

| Property | Description |
| - | - |
| **task_type** (str) [ReadOnly] | The task type managed by this instance |


### <a id="queueing-usage"></a>Task Queueing

#### *class* AppTasking.**TaskQueue**(*task_type="thread", logger_name=""*)

| Argument | Description |
| - | - |
| **task_type** (str) | The type of tasks ("thread", "process") to be supported by this Queuing instance. "process" works with both threads and process so is safer, but has more overhead. Default = "process" |
| **logger_name** (str) | The name of the logger to use.  If empty (or not a string) then a logger will be created to log to the console |

| Property | Description |
| - | - |
| **task_type** (str) [ReadOnly] | The task type supported by this instance |
| **listener_running** (bool) [ReadOnly] | Property indicating if the listener is running |


**put(** item=None, block=True, timeout=None **)**

> Put a message on the queue.

> | Argument | Description |
> | - | - |
> | **item** (Any) | The data to be sent |
> | **block** (bool) | If True block until message can be placed on queue. If false, return immediately and raise exception (#queue.full#) on error. |
> | **timeout** (float | None) | If block is True, time (in seconds) to block before raising exception. |


**get(** block=True, timeout=None **)**

> Return the item previously placed on the queue.

> | Argument | Description |
> | - | - |
> | **block** (bool) | If True block until message is retrieved. If false, return immediately and raise exception (#queue.empty#) if no message found. |
> | **timeout** (float | None) | If block is True, time (in seconds) to block before raising exception. |


**cleanup()**

> Remove all messages from the queue.


**listener(** message_handler=None, keepalive_interval=0 **)**

> Listen for messages on the queue and hand off to the message_handler when they arrive.

> | Argument | Description |
> | - | - |
> | **message_handler** (Callable | None) | Callable to process the received message. The message handler should accept a single parameter - #item# - The data retrieved from the queue. No return value is expected from the message handler. |
> | **keepalive_interval** (int) | Interval within which a keepalive or other message must be received. If 0, defaults to MAX_KEEPLAIVE_INTERVAL. |


**listener_stop()**

> Stop the listener.



```python
import apptasking
# Example usage of AppTasking components
```

## Development

1. Clone the repository:
    ```bash
    git clone https://github.com/JasonPiszcyk/AppTasking.git
    cd AppNetComms
    ```
2. Install dependencies:
    ```bash
    pip install -e .[dev]
    ```

## Running Tests

```bash
pytest
```


## Contributing

Contributions are welcome! Please submit issues or pull requests via [GitHub Issues](https://github.com/JasonPiszcyk/AppTasking/issues).


## License

GNU General Public License


## Author

Jason Piszcyk  
[Jason.Piszcyk@gmail.com](mailto:Jason.Piszcyk@gmail.com)


## Links

- [Homepage](https://github.com/JasonPiszcyk/AppTasking)
- [Bug Tracker](https://github.com/JasonPiszcyk/AppTasking/issues)
