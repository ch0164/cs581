# Filename: dump_truck_operation.py
# Author: Christian Hall
# Date: 11/4/2022
# Description: This file contains the logic for implementing the
#              Dump Truck Operation DES model.

# Python Imports
from typing import Any, Dict, List, Tuple

# Third-Party Imports
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Custom Imports
from source.constants import *
from source.events import ArrivalLoadingQueue, EndLoading, EndWeighing, End
import source.future_event_list as fel
import source.random_variate_generators as rvg


def dump_truck_operation(trial: int,
                         variates: Dict[str, int],
                         probabilities: Dict[str, float],
                         truck_count: int = 8,
                         end_time: int = 240) -> Tuple[float, float, List[str]]:
    """
    Run a single trial of the Dump Truck Operation DES model.
    :param trial: The index of the current trial.
    :param variates: The variates for all three kinds of events.
    :param probabilities: The corresponding probabilities for those events.
    :param truck_count: The number of trucks for the simulation.
    :param end_time: The simulation end time.
    :return: A tuple containing the loader and scale utilization ratios, as
    well as the output for the trial.
    """
    # Keep some statistics of the simulation.
    statistics = {
        "total_busy_loaders": 0,
        "total_busy_scale": 0,
    }

    # Maintain queues for the loaders and scale.
    queue = {
        "L": [],
        "W": []
    }

    # Maintain a dataframe for the system states.
    header = ["clock", "LQ", "L", "WQ", "W", TRAVEL]
    state = {col: 0 for col in header}
    state[TRAVEL] = truck_count
    states = pd.DataFrame(columns=header)
    states.loc[len(states)] = state

    def get_travel_count() -> int:
        """
        Calculate the number of trucks travelling in the system.
        :return: The number of trucks travelling in the system.
        """
        return truck_count - \
               (state["LQ"] + state["L"] + state["WQ"] + state["W"])

    def handle_alq_event(dump_truck_index: int) -> None:
        """
        Handles the logic for ArrivalLoadingQueue (ALQ) events.
        :param dump_truck_index: The index for the dump truck entity.
        :return:
        """
        # Check if there is an idle loader available.
        if state["L"] < 2:
            # Schedule an EndLoading event for this dump truck.
            state["L"] += 1
            service_time = rvg.empirical(variates[EL], probabilities[EL])
            event = EndLoading(id=dump_truck_index,
                               time=state["clock"] + service_time
                               )
            fel.insert_with_priority(event)
        # If no idle loader, then put this dump truck on the loading queue.
        else:
            state["LQ"] += 1
            queue["L"].append(dump_truck_index)

    def handle_el_event(dump_truck_index: int) -> None:
        """
        Handles the logic for EndLoading (EL) events.
        :param dump_truck_index: The index for the dump truck entity.
        :return:
        """
        state["L"] -= 1  # Loading finished, make one loader available.

        # Check if the scale is available.
        if state["W"] == 0:
            # Schedule an EndWeighing event for this dump truck.
            state["W"] = 1
            service_time = rvg.empirical(variates[EW], probabilities[EW])
            event = EndWeighing(id=dump_truck_index,
                                time=state["clock"] + service_time
                                )
            fel.insert_with_priority(event)
        # If unavailable, then put this dump truck on the weighing queue.
        else:
            state["WQ"] += 1
            queue["W"].append(dump_truck_index)

        # Check if there are any dump trucks in the loading queue.
        if state["LQ"] > 0:
            # Take the first dump truck from the queue and schedule
            # an EndLoading event for it.
            next_dump_truck_index = queue["L"].pop(0)
            state["LQ"] -= 1
            state["L"] += 1
            service_time = rvg.empirical(variates[EL],
                                         probabilities[EL])
            event = EndLoading(id=next_dump_truck_index,
                               time=state["clock"] + service_time
                               )
            fel.insert_with_priority(event)

    def handle_ew_event(dump_truck_index: int) -> None:
        """
        Handles the logic for EndWeighing (EW) events.
        :param dump_truck_index: The index for the dump truck entity.
        :return:
        """
        state["W"] = 0  # Weighing finished, make the scale available.

        # Send this dump truck to travel for some time in the system.
        delay = rvg.empirical(variates[TRAVEL], probabilities[TRAVEL])
        event = ArrivalLoadingQueue(id=dump_truck_index,
                                    time=state["clock"] + delay
                                    )
        fel.insert_with_priority(event)

        # Check if there are any dump trucks in the weighing queue.
        if state["WQ"] > 0:
            # Take the first dump truck from the queue and schedule
            # an EndWeighing event for it.
            next_dump_truck_index = queue["W"].pop(0)
            state["WQ"] -= 1
            state["W"] = 1
            service_time = rvg.empirical(variates[EW], probabilities[EW])
            event = EndWeighing(id=next_dump_truck_index,
                                time=state["clock"] + service_time
                                )
            fel.insert_with_priority(event)

    # Initialize the FEL with the dump trucks.
    fel.clear()
    for index in range(truck_count):
        fel.insert_with_priority(ArrivalLoadingQueue(id=index + 1, time=index))
    fel.insert_with_priority(End(time=end_time))

    # Enter the main loop of the simulation.
    previous_event = ArrivalLoadingQueue(id=truck_count, time=truck_count - 1)
    while True:
        current_event = fel.get_next()

        # Collect statistics.
        delta_time = current_event.time - previous_event.time
        state["clock"] = current_event.time
        statistics["total_busy_loaders"] += delta_time * state["L"]
        statistics["total_busy_scale"] += delta_time * state["W"]

        # Handle event logic.
        if current_event.type is ALQ:
            handle_alq_event(current_event.id)
        elif current_event.type is EL:
            handle_el_event(current_event.id)
        elif current_event.type is EW:
            handle_ew_event(current_event.id)
        elif current_event.type is END:
            break
        else:
            print("ERROR: Reached impossible state.")
            exit(1)

        # Save the current state and the previous event.
        state[TRAVEL] = get_travel_count()
        states.loc[len(states)] = state
        previous_event = current_event

    # Get the utilization ratios for this trial.
    loader_utilization = statistics["total_busy_loaders"] / (2 * end_time)
    scale_utilization = statistics["total_busy_scale"] / end_time

    # Plot only the first trial.
    if trial == 1:
        plot_states(states, truck_count, end_time)

    # Produce output of the trial.
    execution_parameters = {
        "scenario": "2 Notional",
        "simulation_run_length": end_time,
        "number_trucks": truck_count,
    }
    calculated_statistics = {
        "loader_utilization": loader_utilization,
        "scale_utilization": scale_utilization,
    }
    output = format_output(trial,
                           "Multi-queue, multi-server - Dump Truck Operation",
                           execution_parameters,
                           calculated_statistics)
    return loader_utilization, scale_utilization, output


def plot_states(states: pd.DataFrame,
                truck_count: int,
                end_time: int) -> None:
    """
    Produce a plot that resembles the given plot for the Dump Truck Operation.
    :param states: The dataframe containing the system's state at every
    time step.
    :param truck_count: The number of trucks for the simulation.
    :param end_time: The simulation end time.
    :return:
    """
    colors = ["blue", "purple", "green", "red", "gold"]
    columns = ["LQ", "L", "WQ", "W", TRAVEL]

    # Manipulate the plot labels and dimensions.
    plt.title("Christian Hall")
    plt.xlabel("Time")
    plt.ylabel("Trucks")
    plt.xlim(left=-5, right=end_time + 5)
    plt.ylim(bottom=-0.5, top=truck_count + 1)
    plt.xticks([time for time in range(0, 244, 30)])
    plt.yticks([truck for truck in range(truck_count + 1)])
    plt.margins(x=5, y=0.3)

    # Plot the dashed, gray vertical lines representing each event start.
    for clock in states["clock"].values:
        plt.axvline(clock, alpha=0.3, ls="--", color="gray")

    # Plot the differing system states for each truck over time.
    plot_offsets_x = np.array([-2, -1, 0, 1, 2]) * 0.25
    plot_offsets_y = np.array([2, 1, 0, -1, -2]) * 0.05
    for column, color, offset_x, offset_y in zip(
            columns, colors, plot_offsets_x, plot_offsets_y):
        plt.step(states["clock"] + offset_x,
                 states[column] + offset_y,
                 label=column, color=color, marker="o",
                 markersize=4,
                 alpha=0.5,
                 where="post")

    # Put down the legend and save the figure.
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIRECTORY}dump_truck_operation_trial_1_plot.png")


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
        format_str = f"\t\t{key.replace('_', ' ').capitalize():<45}"
        format_str += f"{value}"
        if "length" in key:
            format_str += " minutes"
        lines.append(format_str)
    lines.append("")
    lines.append("\tCalculated statistics")
    for key, value in statistics.items():
        format_str = f"\t\t{key.replace('_', ' ').capitalize():<45}"
        format_str += f"{value:.4f}"
        lines.append(format_str)
    lines.append("")

    return lines


def main():
    # List of random variates and probabilities for the three event types.
    variates = {
        EL: [5, 10, 15],
        EW: [12, 16],
        TRAVEL: [40, 60, 80, 100],
    }
    probabilities = {
        EL: [0.3, 0.5, 0.2],
        EW: [0.7, 0.3],
        TRAVEL: [0.4, 0.3, 0.2, 0.1],
    }

    # Run 100 trials of the Airport Check-In DES model.
    trial_count = 100
    trials = [dump_truck_operation(trial_index, variates, probabilities)
              for trial_index in range(1, trial_count + 1)]

    # Output all trials of the simulation, as well as the mean utilizations.
    with open(f"{OUTPUT_DIRECTORY}dump_truck_operation.txt", "w") as fp:
        loader_utilizations = []
        scale_utilizations = []
        for loader_utilization, scale_utilization, output in trials:
            loader_utilizations.append(loader_utilization)
            scale_utilizations.append(scale_utilization)
            for lines in output:
                fp.writelines(lines + "\n")
        fp.write(f"Dump Truck Operation, scenario= 2 "
                 f"trials= {trial_count}\n")
        loader_average = sum(loader_utilizations) / len(loader_utilizations)
        scale_average = sum(scale_utilizations) / len(scale_utilizations)
        fp.write(f"\tMean loader utilization= {loader_average:.4f}\n")
        fp.write(f"\tMean scale utilization= {scale_average:.4f}\n")


if __name__ == "__main__":
    main()
