import pathlib as _pl

import data_structures
from pytrnsys_process import api


def processing_step_1(simulation: data_structures.Simulation):
    """The simulation property provides you access to hourly, monthly and step data.
    Use this processing step to plot your data or process to your needs"""


def processing_step_2(simulation: data_structures.Simulation):
    """You can define as many processing steps as you want.
    Splitting your processing into multiple steps is useful if something goes wrong in one of your steps.
    The other steps will still be processed."""


def main():
    # bundle the scenarios into a list
    processing_steps = [
        processing_step_1,
        processing_step_2,
    ]
    path_to_single_sim = _pl.Path("path/to/simulation")
    path_to_results_set = _pl.Path("path/to/result/set")

    # to run a SINGLE processing step on a single simulation
    api.process_single_simulation(
        path_to_single_sim,
        processing_step_1,
    )

    # to run ALL processing steps on a single simulation
    api.process_single_simulation(
        path_to_single_sim,
        processing_steps,
    )

    # to run ALL processing steps on a whole result set
    api.process_whole_result_set(
        path_to_results_set,
        processing_steps,
    )

    # to run ALL processing steps on a whole result set in parallel
    api.process_whole_result_set_parallel(
        path_to_results_set,
        processing_steps,
    )


if __name__ == "__main__":
    main()
