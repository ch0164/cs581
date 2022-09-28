import future_event_list as fel
from events import Arrival, Departure, End
import random


def main():
    for index in range(100):
        time = random.randint(1, 500)
        event_type = random.choice([Arrival, Departure])
        event = event_type(time)
        fel.insert_with_priority(event)
    fel.display()

if __name__ == "__main__":
    main()