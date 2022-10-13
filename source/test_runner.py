# Filename: test_runner.py
# Author: Christian Hall
# Date: 09/28/2022
# Description: This file is the driver for running unit tests.

# Python Imports
from datetime import datetime
import logging
import unittest
import time

# Test Imports
import test_future_event_list

if __name__ == "__main__":
    # Get the logger and start time of the run.
    logger = logging.getLogger(__name__)
    now = datetime.now()
    start = time.perf_counter()
    logger.info(f"START: Future Event List Test, {now.date()} {now.time()}")

    # Run the suite of tests.
    suite = unittest.TestLoader().loadTestsFromModule(test_future_event_list)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)

    # End of tests.
    end = time.perf_counter()
    logger.info(f"END: Future Event List, {now.date()} {now.time()}")
    logger.info(f"Total Run Time: {end - start} s")
