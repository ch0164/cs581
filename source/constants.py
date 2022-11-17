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

# CFA Directories
CFA_DIRECTORY = ROOT_DIRECTORY + "cv_cfa/"
CFA_DATA = CFA_DIRECTORY + "data/"
CFA_FIGURE_DIRECTORY = CFA_DIRECTORY + "figures/"

# CFA Data Files
CFA_TIMESTAMPS_FILE = CFA_DATA + "cv_cfa_timestamps.csv"
CFA_STATISTICS_FILE = CFA_DATA + "cv_cfa_statistics.csv"

# ------------------------------------------------------------------------------
# Event Constants
# ------------------------------------------------------------------------------
ARRIVAL = "ARRIVAL"
DEPARTURE = "DEPARTURE"

ALQ = "ALQ"
EL = "EL"
EW = "EW"
TRAVEL = "Travel"

END = "END"

# ------------------------------------------------------------------------------
# Entity Constants
# ------------------------------------------------------------------------------
IDLE = "IDLE"
BUSY = "BUSY"

DUMP_TRUCK = "DUMP_TRUCK"

# ------------------------------------------------------------------------------
# DES Model Specific Constants
# ------------------------------------------------------------------------------
# Grocery Check-In
ALLOW_TRANSFERS = "ALLOW"
PROHIBIT_TRANSFERS = "PROHIBIT"
FIRST_CLASS = "FIRST_CLASS"
ECONOMY_CLASS = "ECONOMY"

# Charger Village CFA
STATISTICS_HEADERS = [
    "interarrival_time",
    "response_rate",
    "cashier_service_time",
    "counter_service_time",
    "food_delay",
    "drink_delay",
    "enter_queue_delay",
]

# ------------------------------------------------------------------------------
# Heap Implementation Constants
# ------------------------------------------------------------------------------
CUSTOM_HEAP = "Custom Min Heap"
PYTHON_HEAP = "heapq Min Heap"

# ------------------------------------------------------------------------------
# Test Constants
# ------------------------------------------------------------------------------
LOG_FILE = lambda name: f"{name}_log.txt"
