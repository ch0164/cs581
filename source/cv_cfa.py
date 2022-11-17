# Filename: cv_cfa.py
# Author: Christian Hall
# Date: 11/17/2022
# Description: This file contains the logic for implementing the
#              Charger Village Chick-Fil-A DES model.

# Python Imports
from typing import Any, Dict, List, Tuple

# Third-Party Imports
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

# Custom Imports
from source.constants import *
import source.future_event_list as fel
import source.random_variate_generators as rvg


def output_statistics_file() -> None:
    """
    Generate the statistics file and write it to the data directory.
    :return:
    """
    # Read the recorded timestamps as datetimes.
    times_df: pd.DataFrame = pd.read_csv(CFA_TIMESTAMPS_FILE)
    for column in times_df.columns:
        times_df[column] = pd.to_datetime(times_df[column])

    # Populate the statistics dataframe with timedeltas.
    stats_df = pd.DataFrame(columns=STATISTICS_HEADERS)
    stats_df["interarrival_time"] = times_df["arrival_time"].diff()

    stats_df["response_rate"] = times_df["cashier_service_end_time"] - \
                                times_df["arrival_time"]

    stats_df["cashier_service_time"] = times_df["cashier_service_end_time"] - \
                                       times_df["cashier_service_start_time"]

    stats_df["counter_service_time"] = times_df["counter_service_end_time"] - \
                                       times_df["counter_service_start_time"]

    stats_df["food_delay"] = times_df["food_delay_end_time"] - \
                             times_df["food_delay_start_time"]

    stats_df["drink_delay"] = times_df["cashier_service_start_time"] - \
                              times_df["cashier_arrival_time"]

    stats_df["enter_queue_delay"] = times_df["front_of_queue_time"] - \
                                    times_df["arrival_time"]


    def strfdelta(td: pd.Timedelta) -> str:
        """
        Represent timedelta objects in minutes.
        :param td: The candidate timedelta.
        :return: The timedelta in minutes, rounded to four decimal places.
        """
        minutes = td.seconds / 60
        return f"{minutes:.4f}"


    # Format the timedelta objects to use minutes as the time unit.
    for column in stats_df.columns:
        try:
            stats_df[column] = stats_df[column].apply(strfdelta)
        # If the entry is nan, skip it.
        except:
            pass

    # Output the finalized statistics file to the data directory.
    stats_df.to_csv(CFA_STATISTICS_FILE, index=False)


def plot_histograms(stats_df: pd.DataFrame) -> None:
    """
    Generate histograms for every statistic to determine their distribution.
    :param stats_df: The dataframe of statistics.
    :return:
    """
    for column in stats_df.columns:
        plt.clf()
        stats_df.hist(column=column, figsize=(10, 8))
        plt.xlabel("Time (minutes)")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(f"{CFA_FIGURE_DIRECTORY}{column}_histogram.png")
        plt.show()


def main() -> None:
    output_statistics_file()
    stats_df = pd.read_csv(CFA_STATISTICS_FILE, dtype=float)
    plot_histograms(stats_df)


if __name__ == "__main__":
    main()
