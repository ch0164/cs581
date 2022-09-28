# Filename:
# Author:
# Description:
# Date:

# Custom Imports
import heapq as hq
from typing import Union

from source.events import *

fel = []


def get_next() -> Event:
    if fel:
        return hq.heappop(fel)


def insert_with_priority(event: Event) -> None:
    hq.heappush(fel, event)


def delete(event: Event) -> None:
    if not fel:
        return
    fel.remove(event)
    hq.heapify(fel)


def length() -> int:
    return len(fel)


def peek() -> Union[None, Event]:
    if not fel:
        return None
    return fel[0]


def clear() -> None:
    global fel
    fel = []


def display(output_file="") -> None:
    print(hq.nsmallest(len(fel), fel))
