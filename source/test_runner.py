# Filename:
# Author: Christian Hall
# Date: 09/28/2022
# Description:

# Python Imports
import unittest

# Test Imports
import test_future_event_list

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromModule(test_future_event_list)
    runner = unittest.TextTestRunner(verbosity=2)
    results = runner.run(suite)
