from source.constants import *


class Event:
    def __init__(self, time):
        self.time = time
        self.type = None

    def __lt__(self, other):
        if self.time == other.time:
            if self.type == END_EVENT:
                return False
            return self.type == ARRIVAL_EVENT
        return self.time < other.time

    def __eq__(self, other):
        return self.time == other.time and self.type == other.type

    def __repr__(self):
        return f"({self.type[0]}, {self.time})"


class Arrival(Event):
    def __init__(self, time):
        super().__init__(time)
        self.type = ARRIVAL_EVENT


class Departure(Event):
    def __init__(self, time):
        super().__init__(time)
        self.type = DEPARTURE_EVENT


class End(Event):
    def __init__(self, time):
        super().__init__(time)
        self.type = END_EVENT
