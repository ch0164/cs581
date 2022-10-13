# Filename: constants.py
# Author: Christian Hall
# Date: 09/28/2022
# Description: This file contains constant values for all programs in CS 581.

# Python Imports
import os

# ------------------------------------------------------------------------------
# Directory Constants
# ------------------------------------------------------------------------------
SOURCE_DIRECTORY = os.getcwd() + "/"
ROOT_DIRECTORY = os.path.abspath(os.path.join(SOURCE_DIRECTORY, os.pardir)) + \
                 "/"
OUTPUT_DIRECTORY = ROOT_DIRECTORY + "output/"

# ------------------------------------------------------------------------------
# Event Constants
# ------------------------------------------------------------------------------
ARRIVAL_EVENT = "ARRIVAL"
DEPARTURE_EVENT = "DEPARTURE"
END_EVENT = "END"

# ------------------------------------------------------------------------------
# Heap Implementation Constants
# ------------------------------------------------------------------------------
CUSTOM_HEAP = "Custom Min Heap"
PYTHON_HEAP = "heapq Min Heap"

# ------------------------------------------------------------------------------
# Test Constants
# ------------------------------------------------------------------------------
LOG_FILE = lambda name: f"{name}_log.txt"
