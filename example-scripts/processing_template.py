import pathlib as _pl

import pytrnsys_process as pp


def processing_scenario(simulation):
    """The simulation property provides you access to hourly, monthly and step data.
    Use this functions body to plot your data or process to your needs"""


if __name__ == "__main__":
    # to process a single simulation
    pp.process_single_simulation(
        _pl.Path("path/to/simulation"),
        processing_scenario,
    )

    # to process a whole result set
    pp.process_whole_result_set(
        _pl.Path("path/to/result/set"),
        processing_scenario,
    )

    # to process a whole result set in parallel
    pp.process_whole_result_set_parallel(
        _pl.Path("path/to/result/set"),
        processing_scenario,
    )
