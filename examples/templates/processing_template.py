import pathlib as _pl

import pytrnsys_process as pp


def processing_step_1(simulation: pp.Simulation):
    """The simulation property provides you access to hourly, monthly and step data.
    Use this processing step to plot your data or process to your needs"""


def processing_step_2(simulation: pp.Simulation):
    """You can define as many processing steps as you want.
    Splitting your processing into multiple steps is useful if something goes wrong in one of your steps.
    The other steps will still be processed."""


if __name__ == "__main__":
    # bundle the scenarios into a list
    processing_steps = [
        processing_step_1,
        processing_step_2,
    ]

    # to run a single processing step on a single simulation
    pp.process_single_simulation(
        _pl.Path("path/to/simulation"),
        processing_step_1,
    )

    # to run the processing steps on a whole result set
    pp.process_whole_result_set(
        _pl.Path("path/to/result/set"),
        processing_steps,
    )

    # to run the processing steps on a whole result set in parallel
    pp.process_whole_result_set_parallel(
        _pl.Path("path/to/result/set"),
        processing_steps,
    )