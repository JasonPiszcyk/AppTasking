#!/usr/bin/env python3
'''
The Constants used for Testing

Copyright (C) 2026 Jason Piszcyk
Email: Jason.Piszcyk@gmail.com

All rights reserved.

This software is private and may NOT be copied, distributed, reverse engineered,
decompiled, or modified without the express written permission of the copyright
holder.

The copyright holder makes no warranties, express or implied, about its 
suitability for any particular purpose.
'''
###########################################################################
#
# Imports
#
###########################################################################
# Shared variables, constants, etc

# System Modules

# Local app modules

# Imports for python variable type hints


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
# Different data type to try out
DATA_SET = {
    "String": { "type": str, "value": "A string to be stored in shared mem" },
    "Integer": { "type": int, "value": 100 },
    "Float": { "type": float, "value": 3.141 },
    "Dict": { 
        "type": dict,
        "value": {
            "value_string": "a string stored in the dict",
            "value_int": 100
        }
    },
    "List": {
        "type": list,
        "value": [ "string in list", 8, "another string" ]
    }
}

DATA_DICT = {
    "type": dict,
    "value": {
        "value_string": "a string stored in the dict",
        "value_int": 100
    }
}


#
# Global Variables
#
