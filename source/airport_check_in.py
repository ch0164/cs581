# Filename: airport_check_in.py
# Author: Christian Hall
# Date: 10/30/2022
# Description: This file contains the logic for implementing the
#              Airport Check-In DES model.

# Python Imports
from typing import Any, Dict, List, Tuple, Union

# Custom Imports
from source.constants import *
from source.events import Arrival, Departure, End
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


def airport_check_in(trial: int,
                     scenario: str,
                     interarrival_mean: Tuple[Union[int, float]] = (2, 1),
                     service_mean: Tuple[Union[int, float]] = (2, 1),
                     service_std: Tuple[Union[int, float]] = (0.5, 0.25),
                     long_response_threshold: Tuple[Union[int, float]] = 4,
                     end_time: int = 120) -> Tuple[float, List[str]]:
    """
    Execute a single trial of the Grocery Checkout DES model.
    :param trial: Trial index.
    :param scenario: Determines whether transfers between the first-class and
    economy-class queues are allowed or not.
    :param interarrival_mean: Average times between arrivals.
    :param service_mean: Average times for servicing entities.
    :param service_std: Standard deviations for servicing entities.
    :param long_response_threshold: Threshold for a service to be considered a
    'long' response.
    :param end_time: End the simulation when this many time units
    (here, minutes) pass.
    :return: A tuple, where the first three elements are the first class,
    economy, and overall mean response times, and the fourth element is
    the formatted output of the trial's execution parameters and
    calculated statistics.
    """
    global uuid
    uuid = -1
    clock = 0
    allow_transfers = True if scenario is ALLOW_TRANSFERS else False
    transfer_count = 0
    statistics = {
        flight_class:
            {
                "arrival_count": 0,
                "departure_count": 0,
                "cumulative_time_busy": 0,
                "current_queue_length": 0,
                "maximum_queue_length": 0,
                "cumulative_response_time": 0,
                "long_response_count": 0,
                "cumulative_interarrival_time": 0,
                "cumulative_service_time": 0,
                "service_started_count": 0,
            } for flight_class in [FIRST_CLASS, ECONOMY_CLASS]}
    states = {
        flight_class:
            {
                "queue": [],
                "server_status": IDLE,

            } for flight_class in [FIRST_CLASS, ECONOMY_CLASS]}
    parameters = {
        flight_class:
            {
                "interarrival_mean": interarrival_mean[index],
                "service_mean": service_mean[index],
                "service_std": service_std[index],
            } for index, flight_class in
        enumerate([FIRST_CLASS, ECONOMY_CLASS])}

    # Initialize FEL with first arrival.
    first_class_event = Arrival(id=get_uuid(), entity=FIRST_CLASS, time=0.0)
    economy_class_event = Arrival(id=get_uuid(), entity=ECONOMY_CLASS, time=0.0)
    end_event = End(time=end_time)
    fel.clear()
    fel.insert_with_priority(first_class_event)
    fel.insert_with_priority(economy_class_event)
    fel.insert_with_priority(end_event)
    previous_event = economy_class_event

    def schedule_arrival(flight_class: str,
                         clock_: Union[int, float]) -> float:
        """
        Schedule an Arrival event onto the FEL.
        :param flight_class: The server of this flight class.
        :param clock_: The current simulation time.
        :return: The randomly generated interarrival time.
        """
        interarrival_time_ = rvg.exponential(
            parameters[flight_class]["interarrival_mean"]
        )
        event = Arrival(id=get_uuid(),
                        entity=flight_class,
                        time=clock_ + interarrival_time_)
        fel.insert_with_priority(event)
        return interarrival_time_

    def schedule_departure(arrival_event_: Arrival,
                           flight_class: str,
                           clock_: Union[int, float]) -> float:
        """
        Schedule a Departure event onto the FEL.
        :param arrival_event_: This departure's corresponding Arrival event.
        :param flight_class: The server of this flight class.
        :param clock_: The current simulation time.
        :return: The randomly generated service time.
        """
        service_time_ = rvg.truncated_normal(
            parameters[flight_class]["service_mean"],
            parameters[flight_class]["service_std"],
            a=0,
        )
        event = Departure(id=arrival_event_.id,
                          entity=flight_class,
                          time=clock_ + service_time_,
                          arrival_time=arrival_event_.time,
                          )
        fel.insert_with_priority(event)
        return service_time_

    # Main loop; process events until end event occurs.
    while previous_event.type is not END:
        current_event = fel.get_next()
        clock = current_event.time

        # Update the time which the servers are busy.
        for flight_class in [FIRST_CLASS, ECONOMY_CLASS]:
            if states[FIRST_CLASS]["server_status"] is BUSY:
                time_busy = current_event.time - previous_event.time
                statistics[flight_class]["cumulative_time_busy"] += time_busy

        # Save the flight class here for easier handling later.
        flight_class = current_event.entity

        # Handle arrival logic.
        if current_event.type is ARRIVAL:
            if states[flight_class]["server_status"] is BUSY:
                states[flight_class]["queue"].append(current_event)
                statistics[flight_class]["current_queue_length"] += 1
            else:
                states[flight_class]["server_status"] = BUSY

                # Schedule a Departure event for this entity.
                service_time = schedule_departure(
                    current_event,
                    flight_class,
                    clock
                )

                # Collect statistics.
                statistics[flight_class]["cumulative_service_time"] += \
                    service_time
                statistics[flight_class]["service_started_count"] += 1

            # Regardless, schedule a new Arrival event.
            interarrival_time = schedule_arrival(
                flight_class,
                clock
            )

            # Collect statistics.
            statistics[flight_class]["cumulative_interarrival_time"] += \
                interarrival_time
            statistics[flight_class]["arrival_count"] += 1
            statistics[flight_class]["maximum_queue_length"] = \
                max(statistics[flight_class]["maximum_queue_length"],
                    statistics[flight_class]["current_queue_length"])

        # Handle departure logic.
        elif current_event.type is DEPARTURE:
            # Collect statistics.
            arrival_time = current_event.arrival_time
            response_time = clock - arrival_time
            if response_time >= long_response_threshold:
                statistics[flight_class]["long_response_count"] += 1
            statistics[flight_class][
                "cumulative_response_time"] += response_time
            statistics[flight_class]["departure_count"] += 1

            # Check if the queue for the current flight class is empty.
            if not states[flight_class]["queue"]:
                # Check if a transfer between flight classes should occur.
                if allow_transfers and flight_class is FIRST_CLASS and \
                        len(states[ECONOMY_CLASS]["queue"]) > 0 and \
                        states[ECONOMY_CLASS]["server_status"] is BUSY:
                    economy_arrival_event = states[ECONOMY_CLASS]["queue"].pop(
                        0)
                    service_time = schedule_departure(
                        economy_arrival_event,
                        FIRST_CLASS,
                        clock
                    )

                    # Collect statistics.
                    statistics[FIRST_CLASS]["cumulative_service_time"] += \
                        service_time
                    statistics[FIRST_CLASS]["service_started_count"] += 1
                    transfer_count += 1
                else:
                    states[flight_class]["server_status"] = IDLE

            # Service the next entity.
            else:
                # Schedule a new Departure event for the next entity.
                arrival_event = states[flight_class]["queue"].pop(0)
                service_time = schedule_departure(
                    arrival_event,
                    flight_class,
                    clock
                )

                # Collect statistics.
                statistics[flight_class]["current_queue_length"] -= 1
                statistics[flight_class]["cumulative_service_time"] += \
                    service_time
                statistics[flight_class]["service_started_count"] += 1

        # Save this event for later.
        previous_event = current_event

    # Get the total number of arrivals, departures, and remaining entities.
    total_arrivals = sum(
        [statistics[flight_class]["arrival_count"]
         for flight_class in [FIRST_CLASS, ECONOMY_CLASS]]
    )
    total_departures = sum(
        [statistics[flight_class]["departure_count"]
         for flight_class in [FIRST_CLASS, ECONOMY_CLASS]]
    )
    total_in_system = total_arrivals - total_departures

    # Construct execution parameters for output.
    for flight_class in [FIRST_CLASS, ECONOMY_CLASS]:
        for key in parameters[flight_class]:
            parameters[flight_class][f"{key}_time"] = \
                parameters[flight_class].pop(key)
    execution_parameters = dict({
        "simulation_run_duration": end_time,
        "transfers_allowed": "Yes" if allow_transfers else "No",
    }, **parameters)

    # Calculate statistics for output.
    calculated_statistics = {flight_class: {
        "number_of_arrivals": statistics[flight_class]["arrival_count"],
        "mean_interarrival_time": statistics[flight_class][
                                      "cumulative_interarrival_time"] /
                                  statistics[flight_class]["arrival_count"],
        "maximum_queue_length": statistics[flight_class][
            "maximum_queue_length"],
        "length_at_simulation_end": statistics[flight_class][
            "current_queue_length"],
        "server_utilization": statistics[flight_class]["cumulative_time_busy"] /
                              clock,
        "number_of_departures": statistics[flight_class]["departure_count"],
        "mean_response_time": statistics[flight_class]
                              ["cumulative_response_time"] /
                              statistics[flight_class]["departure_count"],
        "long_response_ratio": statistics[flight_class]["long_response_count"] /
                               statistics[flight_class]["departure_count"],
        "mean_service_time": statistics[flight_class][
                                 "cumulative_service_time"] /
                             statistics[flight_class]["service_started_count"],
        "status_at_simulation_end": states[flight_class]["server_status"]
    } for flight_class in [FIRST_CLASS, ECONOMY_CLASS]}
    calculated_statistics[FIRST_CLASS]["economy_class_customers_served"] = \
        transfer_count
    calculated_statistics["total_arrivals"] = total_arrivals
    calculated_statistics["total_departures"] = total_departures
    calculated_statistics["total_in_system_at_simulation_end"] = total_in_system

    output = format_output(trial,
                           "Multi-queue, multi-server - Airport Check-In",
                           execution_parameters,
                           calculated_statistics)

    # Return the mean response times and the formatted output.
    overall_mean_response_time = sum(
        [statistics[flight_class]["cumulative_response_time"]
         for flight_class in [FIRST_CLASS, ECONOMY_CLASS]]
    ) / total_departures
    return (calculated_statistics[FIRST_CLASS]["mean_response_time"],
            calculated_statistics[ECONOMY_CLASS]["mean_response_time"],
            overall_mean_response_time,
            output)


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

    for flight_class in [FIRST_CLASS, ECONOMY_CLASS]:
        for key, value in parameters[flight_class].items():
            format_key = f"{flight_class.replace('_', ' ').capitalize()}, " \
                         f"{key.replace('_', ' ').capitalize()}"
            format_str = f"\t\t{format_key:<45}"
            format_str += f"{value}"
            if "time" in key or "duration" in key:
                format_str += " minutes"
            lines.append(format_str)
    for key, value in parameters.items():
        if not isinstance(value, dict):
            format_str = f"\t\t{key.replace('_', ' ').capitalize():<45}"
            format_str += f"{value}"
            if "time" in key or "duration" in key:
                format_str += " minutes"
            lines.append(format_str)
    lines.append("")

    lines.append("\tCalculated statistics")
    for flight_class in [FIRST_CLASS, ECONOMY_CLASS]:
        for key, value in statistics[flight_class].items():
            format_key = f"{flight_class.replace('_', ' ').capitalize()}, " \
                         f"{key.replace('_', ' ').capitalize()}"
            format_str = f"\t\t{format_key:<45}"
            format_str += f"{value:.4f}" if isinstance(value, float) \
                else f"{value}"
            if "time" in key or "duration" in key:
                format_str += " minutes"
            lines.append(format_str)
        lines.append("")
    for key, value in statistics.items():
        if not isinstance(value, dict):
            format_str = f"\t\t{key.replace('_', ' ').capitalize():<45}"
            format_str += f"{value}"
            lines.append(format_str)
    lines.append("")

    return lines


def main():
    # Run 100 trials of the Airport Check-In DES model.
    trial_count = 30
    for scenario in [ALLOW_TRANSFERS, PROHIBIT_TRANSFERS]:
        trials = [airport_check_in(trial_index, scenario)
                  for trial_index in range(1, trial_count + 1)]

        # Write the results of each trial to an output file.
        # Also, write the mean response times from all trials to the file.
        mean_responses = {
            FIRST_CLASS: [],
            ECONOMY_CLASS: [],
            "overall": []
        }
        with open(f"{OUTPUT_DIRECTORY}airport_check_in_"
                  f"{scenario.lower()}_transfers.txt", "w") as fp:
            for first_response, economy_response, overall_response, \
                output in trials:
                for lines in output:
                    fp.writelines(lines + "\n")
                mean_responses[FIRST_CLASS].append(first_response)
                mean_responses[ECONOMY_CLASS].append(economy_response)
                mean_responses["overall"].append(overall_response)
            fp.write(f"Airport Check-In, scenario= {scenario.capitalize()} "
                     f"trials= {trial_count}\n")
            transfers_allowed = "Yes" if scenario is ALLOW_TRANSFERS else "No"
            fp.write(f"\t{'Transfers allowed':<40}{transfers_allowed}\n")
            for key, response_times in mean_responses.items():
                mean_response_time = sum(response_times) / trial_count
                format_key = f"{key.replace('_', ' ').capitalize()}, " \
                             f"mean of mean responses="
                fp.write(f"\t{format_key:<40}")
                fp.write(f"{mean_response_time:.4f}\n")


if __name__ == "__main__":
    main()
