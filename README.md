# AppTasking
Copyright (c) 2026 Jason Piszcyk

Applications Components - Tasking and Multiprocessing

<!-- 
Not yet Published to PyPi
[![PyPI version](https://badge.fury.io/py/appnetcomms.svg)](https://pypi.org/project/appnetcomms/)
[![Build Status](https://github.com/JasonPiszcyk/AppnetComms/actions/workflows/python-app.yml/badge.svg)](https://github.com/JasonPiszcyk/AppNetComms/actions)
 -->

## Overview

**AppTasking** provides an interface to multithreading and multiprocessing, building on top of the standard python libraries.

## Features

**AppTasking** consists of a number of sub-modules, being:
- Multiprocessing
  - A generalised Task interface proving multiprocessing via Process and Threads
    - Task Lifecycle management including starting, stopping and watchdog processing to ensure task state

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

### <a id="shared-mem-usage"></a>Shared Mem

#### *class* AppTasking.**Tasking**(*task_type="thread", process_method="spawn", logger_name="", logger_level="CRITICAL"*)

| Argument | Description |
| - | - |
| **task_type** (str) | The type of task ("thread", "process") to be created and managed by this instance. Default = "thread" |
| **process_method** (str) | When task_type is "process", specify the method to created new processes. Valid values are "spawn", "fork", "forkserver". Default = "spawn". For more details, see: https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods |
| **logger_name** (str) | The name of the logger to use.  If empty (or not a string) then a logger will be created to log to the console |
| **logger_level** (str) | If no logger name is provided, the created logger will be set to log events at or above this level (default = "CRITICAL") |

| Property | Description |
| - | - |
| **name** (str) [ReadOnly] | The name of the item/shared memory segment |
| **size** (str) [ReadOnly] | The size of the shared memory segment (which maybe larger than the requested size when it was created) |


**open()**

> Connect to the shared memory segment (if is has been closed) or create a new segment (if it has never been created or has been unlinked). This is called automatically when the instance is created.


**close()**

> Disconnect from shared memory segment.


**delete()**

> Disconnect from shared memory segment and delete it. The segment will no longer be accessible for remote processes.


**get()**
> Get the raw value (in bytes) from the shared memory segment.


**set(** value=b"" **)**

> Store a value in the shared memory segment. The segment is locked during the write of the value.

> | Argument | Description |
> | - | - |
> | **value** (bytes) | The raw value, in bytes, to store in the shared memory segment |






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
