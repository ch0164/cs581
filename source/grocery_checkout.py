# Filename: grocery_checkout.py
# Author: Christian Hall
# Date: 10/13/2022
# Description: This file contains the logic for implementing the
#              Grocery Checkout DES model.

# Python Imports
from typing import Any, Dict, List, Tuple

# Custom Imports
from source.constants import *
from source.events import Arrival, Departure
import source.future_event_list as fel
import source.random_variate_generators as rvg

# Global Variables
uuid = -1


def get_uuid() -> int:
    """
    Generates a new UUID.
    :return: A UUID as an integer.
    """
    global uuid
    uuid += 1
    return uuid


def grocery_checkout(trial: int,
                     interarrival_mean: float = 4.5,
                     service_mean: float = 3.2,
                     service_std: float = 0.6,
                     long_response_threshold: float = 4.0,
                     customer_limit: int = 1000) -> Tuple[float, List[str]]:
    """
    Execute a single trial of the Grocery Checkout DES model.
    :param trial: Trial index.
    :param interarrival_mean: Average time between arrivals.
    :param service_mean: Average time for servicing customers.
    :param service_std: Standard deviation for servicing customers.
    :param long_response_threshold: Threshold for a service to be considered
    a 'long' response.
    :param customer_limit: End the simulation when this many customers depart.
    :return: A tuple, where the first element is the mean response time,
    and the second element is the formatted output of the trial's execution
    parameters and calculated statistics.
    """
    clock = 0
    server = IDLE
    queue = []
    statistics = {
        "arrival_count": 0,
        "departure_count": 0,
        "cumulative_delay": 0,
        "cumulative_time_busy": 0,
        "current_queue_length": 0,
        "maximum_queue_length": 0,
        "cumulative_response_time": 0,
        "long_response_count": 0,
        "cumulative_interarrival_time": 0,
        "cumulative_service_time": 0,
        "service_started_count": 0,
    }

    # Initialize FEL with first arrival.
    event = Arrival(id=get_uuid(), time=0.0)
    fel.clear()
    fel.insert_with_priority(event)
    previous_event = event

    # Main loop; process events until departure limit.
    while statistics["departure_count"] < customer_limit:
        current_event = fel.get_next()
        clock = current_event.time

        # Update the time which the server is busy.
        if server is BUSY:
            time_busy = current_event.time - previous_event.time
            statistics["cumulative_time_busy"] += time_busy

        # Handle arrival logic.
        if current_event.type is ARRIVAL:
            # Add this customer to the queue if the server is busy.
            if server is BUSY:
                # Update the queue.
                statistics["current_queue_length"] += 1
                queue.append((current_event.id, current_event.time))

            # Otherwise, service this customer.
            else:
                server = BUSY

                # Generate a Departure event for this customer.
                service_time = rvg.truncated_normal(service_mean,
                                                    service_std,
                                                    a=0)
                event = Departure(id=current_event.id,
                                  time=clock + service_time,
                                  arrival_time=current_event.time)
                fel.insert_with_priority(event)

                # Collect statistics.
                statistics["cumulative_service_time"] += service_time
                statistics["service_started_count"] += 1

            # Regardless, generate a new Arrival event.
            interarrival_time = rvg.exponential(interarrival_mean)
            event = Arrival(id=get_uuid(), time=clock + interarrival_time)
            fel.insert_with_priority(event)

            # Collect statistics.
            statistics["cumulative_interarrival_time"] += interarrival_time
            statistics["arrival_count"] += 1
            statistics["maximum_queue_length"] = \
                max(statistics["maximum_queue_length"],
                    statistics["current_queue_length"])

        # Handle departure logic.
        elif current_event.type is DEPARTURE:
            # Collect statistics.
            arrival_time = current_event.arrival_time
            response_time = clock - arrival_time
            if response_time >= long_response_threshold:
                statistics["long_response_count"] += 1
            statistics["cumulative_response_time"] += response_time
            statistics["departure_count"] += 1

            # The server is idle when there are no customers in the queue.
            if statistics["current_queue_length"] <= 0:
                server = IDLE

            # Service the next customer.
            else:
                # Generate a new Departure event for the next customer in line.
                service_time = rvg.normal(service_mean, service_std)
                event_id, arrival_time = queue.pop()
                event = Departure(id=event_id,
                                  time=clock + service_time,
                                  arrival_time=arrival_time)
                fel.insert_with_priority(event)

                # Collect statistics.
                statistics["current_queue_length"] -= 1
                statistics["cumulative_service_time"] += service_time
                statistics["service_started_count"] += 1

        # Save this event for later.
        previous_event = current_event

    # Get formatted output.
    mean_response_time = \
        statistics["cumulative_response_time"] / statistics["departure_count"]
    parameters = {
        "mean_interarrival_time": interarrival_mean,
        "mean_service_time": service_mean,
        "std_dev_service_time": service_std,
        "number_of_customers_served": customer_limit
    }
    calculated_statistics = {
        "server_utilization": statistics["cumulative_time_busy"] / clock,
        "maximum_queue_length": statistics["maximum_queue_length"],
        "mean_response_time": mean_response_time,
        "long_response_ratio": statistics["long_response_count"] /
                               statistics["departure_count"],
        "simulation_run_duration": clock,
        "number_of_arrivals": statistics["arrival_count"],
        "number_of_departures": statistics["departure_count"],
        "mean_interarrival_time": statistics["cumulative_interarrival_time"] /
                                  statistics["arrival_count"],
        "mean_service_time": statistics["cumulative_service_time"] /
                             statistics["service_started_count"],
    }
    output = format_output(trial,
                           "Single-queue, single-server - Grocery Checkout",
                           parameters,
                           calculated_statistics)

    # Return the mean response time and the formatted output.
    return mean_response_time, output


def format_output(trial: int,
                  model_name: str,
                  parameters: Dict[str, Any],
                  statistics: Dict[str, Any]) -> List[str]:
    """
    Format the output of one trial of a DES model.
    :param trial: The trial number.
    :param model_name: The name of the model.
    :param parameters: The execution parameters of the model.
    :param statistics: The calculated statistics of the model.
    :return: The formatted output as a list of strings (no newlines).
    """
    lines = [
        model_name,
        f"trial= {trial}",
        "\tExecution parameters"
    ]

    for key, value in parameters.items():
        format_str = f"\t\t{key.replace('_', ' ').capitalize():<35}\t"
        format_str += f"{value}"
        if "time" in key:
            format_str += " minutes"
        lines.append(format_str)
    lines.append("")

    lines.append("\tCalculated statistics")
    for key, value in statistics.items():
        format_str = f"\t\t{key.replace('_', ' ').capitalize():<35}\t"
        format_str += f"{value}" if isinstance(value, int) else f"{value:.4f}"
        if "time" in key or "duration" in key:
            format_str += " minutes"
        lines.append(format_str)
    lines.append("")

    return lines


def main():
    # Run 30 trials of the Grocery Checkout DES model.
    trial_count = 30
    trials = [grocery_checkout(trial_index)
              for trial_index in range(1, trial_count + 1)]

    # Write the results of each trial to an output file.
    # Also, write the mean response time from all trials to the file.
    mean_response_times = []
    with open(f"{OUTPUT_DIRECTORY}grocery_checkout.txt", "w") as fp:
        for mean_response_time, output in trials:
            mean_response_times.append(mean_response_time)
            for lines in output:
                fp.writelines(lines + "\n")
        fp.write(f"Mean response time over {trial_count} trials: "
                 f"{sum(mean_response_times) / len(mean_response_times):.4f}"
                 f" minutes")


if __name__ == "__main__":
    main()
