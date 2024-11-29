import pathlib as _pl

import pytrnsys_process as pp


def processing_scenario(simulation):
    """The simulation property provides you access to hourly, monthly and step data.
    Use this functions body to plot your data or process to your needs"""
    pass


def processing_scenario_2(simulation):
    pass


def processing_of_energy_balances(simulation):
    pp.bar_chart(simulation.monthly, ["var1", "var2"])

    pass


def processing_of_temperature_histograms(simulation):
    pass


if __name__ == "__main__":
    # Gathering individual processing steps, so that:
    # - each step can fail and other steps will still continue after such a failure.
    # - it is easier to debug individual steps.
    # - invidual steps can be tweaked by themselves after processing.
    processing_steps = [
        processing_of_energy_balances,
        processing_of_temperature_histograms,
        processing_scenario,
        processing_scenario_2,
    ]

    # to run all steps on a single simulation
    pp.process_single_simulation(
        _pl.Path("path/to/simulation"),
        processing_steps,
    )

    # to process a whole result set
    pp.process_whole_result_set(
        _pl.Path("path/to/result/set"),
        processing_steps,
    )

    # to process a whole result set in parallel
    pp.process_whole_result_set_parallel(
        _pl.Path("path/to/result/set"),
        processing_steps,
    )

    # to run a single step on a single simulation
    pp.process_single_simulation(
        _pl.Path("path/to/simulation"),
        processing_scenario,
    )
