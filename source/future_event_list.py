# Filename: future_event_list.py
# Author: Christian Hall
# Date: 09/28/2022
# Description: This file contains the logic implementing the Future Event List
#              data structure.
#              Depending on the value of HEAP_IMPLEMENTATION, the FEL will
#              either use the built-in heapq Python module or the min_heap.py
#              module (which is not built-in).


# Custom Imports
from source.constants import CUSTOM_HEAP, PYTHON_HEAP
from source.events import *

# Check which min-heap implementation to use; default is to use custom one.
import source.flags
if source.flags.HEAP_IMPLEMENTATION == PYTHON_HEAP:
    import heapq as hq
else:
    source.flags.HEAP_IMPLEMENTATION = CUSTOM_HEAP
    import source.min_heap as hq
print(f"Using {source.flags.HEAP_IMPLEMENTATION}")


# Store the Future Event List as a global variable.
fel = []


def get_next() -> Event:
    """
    Return and remove the next Event in the FEL.

    :return: The next Event in the FEL.
    """
    if fel:
        return hq.heappop(fel)


def insert_with_priority(event: Event) -> None:
    """
    Insert a new Event into the FEL and maintain priority.

    :param event: The Event to be inserted.
    :return: None.
    """
    hq.heappush(fel, event)


def delete(event: Event) -> None:
    """
    Delete an Event from the FEL.

    :param event: The Event to be deleted.
    :return: None.
    """
    global fel

    # If the FEL is empty, exit prematurely.
    if not fel:
        return

    # Filter out the Event to be deleted and restore the list as a heap.
    fel = list(filter(lambda e: e not in [event], fel))
    hq.heapify(fel)


def length() -> int:
    """
    Get the length of the FEL.

    :return: The current length of the FEL.
    """
    return len(fel)


def peek() -> Union[None, Event]:
    """
    Return and next Event in the FEL without removing it.

    :return: The next Event in the FEL.
    """
    if not fel:
        return None
    return fel[0]


def clear() -> None:
    """
    Clear the FEL of its contents.

    :return: None.
    """
    global fel
    fel = []


def print_fel(logger) -> None:
    logger.info("FEL Begin")
    for event in hq.nsmallest(len(fel), fel):
        logger.info(f"event={event}")
    logger.info("FEL End")
