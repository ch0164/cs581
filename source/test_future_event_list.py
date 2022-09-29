# Filename:
# Author: Christian Hall
# Date: 09/28/2022
# Description:

# Python Imports
import inspect
import logging
import random
from types import FrameType
import unittest

# Custom Imports
from source.constants import *
from source.events import Arrival, Departure, End

# Set appropriate flags before importing the rest.
import source.flags

source.flags.HEAP_IMPLEMENTATION = CUSTOM_HEAP
# source.flags.HEAP_IMPLEMENTATION = PYTHON_HEAP

# Future Event List Import
# Will use whatever implementation it is set to.
import future_event_list as fel


def print_passed(frame: FrameType) -> None:
    test_case = inspect.getframeinfo(frame).function
    print(PASS_LOG_MESSAGE(test_case))


class TestFutureEventList(unittest.TestCase):
    """This class contains the unit tests for the Future Event List."""

    def test_01_insert_then_get_next(self, operation_count: int = 100):
        time = 0
        prev_time = 0
        get_nexts = 0

        # Insert event_count event notices with random times.
        for index in range(operation_count):
            event_type = random.choice([Arrival, Departure, End])
            event = event_type(index, time)
            fel.insert_with_priority(event)
            time += random.randint(0, 5)

        self.assertEqual(operation_count, fel.length(),
                         f"The FEL should have {operation_count} events.")

        # Pop events off the FEL until it is empty.
        # There should be an equal number of events popped off as there were
        # pushed in, and all events should be in ascending time order.
        while event := fel.get_next():
            self.assertLessEqual(prev_time, event.time,
                                 f"Events should be in ascending time order.")
            prev_time = event.time
            get_nexts += 1
        self.assertEqual(get_nexts, operation_count,
                         f"Number of events deleted does not match number"
                         f"of events inserted.")
        fel.clear()

    def test_02_intermixed_insert_and_get_next(self,
                                               operation_count: int = 100):
        inserts = 0
        get_nexts = 0
        prev_time = 0

        # Randomly perform get_next and insert_with_priority.
        for index in range(operation_count):
            r = random.random()
            if r < 0.4 and fel.length() > 0:
                event = fel.get_next()
                self.assertGreaterEqual(event.time, prev_time,
                                     f"Events should be in ascending time order.")
                prev_time = event.time
                get_nexts += 1
            else:
                event = Arrival(index, prev_time + random.randint(0, 5))
                fel.insert_with_priority(event)
                inserts += 1

        self.assertEqual(inserts + get_nexts, operation_count,
                         f"Unexpected number of operations performed.")
        self.assertEqual(inserts - get_nexts, fel.length(),
                         f"Length of FEL does not match expected length.")
        fel.clear()


    def test_03_hardcoded_insert_and_delete(self) -> None:
        # Following the R code, insert six Events.
        fel.insert_with_priority(Departure(time=10, id=1))
        fel.insert_with_priority(Arrival(time=20, id=2))
        fel.insert_with_priority(Departure(time=30, id=3))
        fel.insert_with_priority(Arrival(time=40, id=4))
        fel.insert_with_priority(Arrival(time=30, id=5))
        fel.insert_with_priority(Arrival(time=20, id=6))

        # Then, delete 4 events.
        fel.delete(Departure(time=10))  # Deletes 1
        fel.delete(Departure(time=30))  # Deletes 3
        fel.delete(Arrival(time=20))  # Deletes 2 and 6
        fel.delete(Departure(time=40))  # Not deleted

        expected_events = [Arrival(time=30), Arrival(time=40)]
        observed_events = []
        while event := fel.get_next():
            observed_events.append(event)
        self.assertEqual(expected_events, observed_events,
                         f"Expected order of events do not match the"
                         f"observed order of events.")
