# Filename:
# Author:
# Description:
# Date:

# Python Imports
import random

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


RANDOM_STATE = 7


def main():
    random.seed(RANDOM_STATE)
    for index in range(100):
        time = random.randint(1, 500)
        event_type = random.choice([Arrival, Departure, End])
        event = event_type(time)
        fel.insert_with_priority(event)

    # for index in range(50):
    #     print(fel.get_next())

    fel.display()


if __name__ == "__main__":
    main()
