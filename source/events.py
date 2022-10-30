# Filename: events.py
# Author: Christian Hall
# Date: 09/28/2022
# Description: This file contains all Events used in programs for CS 581.

# Python Imports
from typing import Union

# Custom Imports
from source.constants import ARRIVAL, DEPARTURE, END


class Event:
    """Base Event class."""
    def __init__(self, id: int = None, entity: str = None,
                 time: Union[int, float] = 0):
        """
        :param id: The ID number of the event.
        :param entity: The entity to which this event belongs.
        :param time: The simulation time of the Event.
        """
        self.id = id
        self.entity = entity
        self.time = time
        self.type = None
        self.arrival_time = None

    def __lt__(self, other: "Event") -> bool:
        """
        :param other: Another Event object.
        :return: Returns True if this Event occurs before the other Event,
                 otherwise returns False.
                 If Events occur at the same time, the priority is as follows:
                 Arrival > Departure > End.
        """
        if self.time == other.time:
            if self.type == END:
                return False
            return self.type == ARRIVAL
        return self.time < other.time

    def __eq__(self, other: "Event") -> bool:
        """
        :param other: Another Event object.
        :return: Returns True if Events have the same fields,
                 otherwise returns False.
        """
        return self.time == other.time and self.type == other.type

    def __repr__(self) -> str:
        """
        :return: String with the format "(<Event Abbreviation>, <Event Time>)".
        """
        return f"(type={self.type[0]}, time={self.time}, id={self.id})"


class Arrival(Event):
    """Arrival Events signify an entity entering into the queueing system."""
    def __init__(self, id: int = None, entity: str = None,
                 time: Union[int, float] = 0):
        """
        :param id: The ID number of the event.
        :param entity: The entity to which this event belongs.
        :param time: The simulation time of the Event.
        """
        super().__init__(id, entity, time)
        self.type = ARRIVAL


class Departure(Event):
    """Departure Events signify an entity exiting from the queueing system."""
    def __init__(self, id: int = None, entity: str = None,
                 time: Union[int, float] = 0,
                 arrival_time: Union[int, float] = 0):
        """
        :param id: The ID number of the event.
        :param entity: The entity to which this event belongs.
        :param time: The simulation time of the Event.
        :param arrival_time: The simulation time of the arrival time for this
        entity.
        """
        super().__init__(id, entity, time)
        self.type = DEPARTURE
        self.arrival_time = arrival_time


class End(Event):
    """End Events signify the end of the simulation."""
    def __init__(self, id: int = None, entity: str = None,
                 time: Union[int, float] = 0):
        """
        :param id: The ID number of the event.
        :param entity: The entity to which this event belongs.
        :param time: The simulation time of the Event.
        """
        super().__init__(id, entity, time)
        self.type = END
