# Filename:
# Author:
# Description:
# Date:

# Python Imports
import sys
from typing import Union

# Custom Imports
from source.events import *

# Check which min-heap implementation to use; default is to use custom one.
import source.flags
if source.flags.HEAP_IMPLEMENTATION == PYTHON_HEAP:
    import heapq as hq
else:
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
    if not fel:
        return
    fel.remove(event)
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


def display(output_file="") -> None:
    """
    Write the contents of the FEL to the screen or an output file.

    :param output_file: If the string is empty, defaults to printing to console.
                        Else, the output will be generated to the output file
                        specified.
    :return: None.
    """
    stdout = None
    if output_file:
        stdout = sys.stdout
        sys.stdout = open(output_file, "w")

    print(hq.nsmallest(len(fel), fel))

    if output_file:
        sys.stdout.close()
        sys.stdout = stdout
