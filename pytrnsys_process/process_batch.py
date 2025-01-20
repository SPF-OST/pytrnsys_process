import pathlib as _pl
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Sequence, Union

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import utils
from pytrnsys_process.logger import logger
from pytrnsys_process.process_sim import process_sim as ps


@dataclass
class ProcessingResults:
    """Results from processing one or more simulations.

    Attributes:
        processed_count: Number of successfully processed simulations
        error_count: Number of simulations that failed to process
        failed_simulations: List of simulation names that failed to process
        failed_scenarios: Dictionary mapping simulation names to lists of failed scenario names
        simulations: Dictionary mapping simulation names to processed Simulation objects

    Example:
        >>> results = ProcessingResults()
        >>> results.processed_count = 5
        >>> results.error_count = 1
        >>> results.failed_simulations = ['sim_001']
        >>> results.failed_scenarios = {'sim_002': ['scenario_1']}
    """

    processed_count: int = 0
    error_count: int = 0
    failed_simulations: List[str] = field(default_factory=list)
    failed_scenarios: dict[str, List[str]] = field(default_factory=dict)
    simulations: dict[str, ps.Simulation] = field(default_factory=dict)
    decks: _pd.DataFrame = field(default_factory=_pd.DataFrame)


def _validate_folder(folder: _pl.Path) -> None:
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")


def _process_simulation(
        sim_folder: _pl.Path,
        processing_scenarios: Union[Callable, Sequence[Callable]],
) -> tuple[ps.Simulation, List[str]]:
    logger.debug("Processing simulation folder: %s", sim_folder)
    sim_files = utils.get_files([sim_folder])
    simulation = ps.process_sim(sim_files, sim_folder)
    failed_scenarios = []

    # Convert single scenario to list for uniform handling
    scenarios = (
        [processing_scenarios]
        if callable(processing_scenarios)
        else processing_scenarios
    )

    for scenario in scenarios:
        try:
            scenario(simulation)
        except Exception as e:  # pylint: disable=broad-except
            scenario_name = getattr(scenario, "__name__", str(scenario))
            failed_scenarios.append(scenario_name)
            logger.error(
                "Scenario %s failed for simulation %s: %s",
                scenario_name,
                sim_folder.name,
                str(e),
                exc_info=True,
            )

    _plt.close("all")
    return simulation, failed_scenarios


def _log_processing_results(results: ProcessingResults) -> None:
    logger.info(
        "Batch processing complete. Processed: %d, Errors: %d",
        results.processed_count,
        results.error_count,
    )
    if results.error_count > 0:
        logger.warning(
            "Some simulations failed to process. Check the log for details."
        )
    if results.failed_scenarios:
        logger.warning(
            "Some scenarios failed: %s",
            {
                sim: scenarios
                for sim, scenarios in results.failed_scenarios.items()
                if scenarios
            },
        )


def process_single_simulation(
        sim_folder: _pl.Path,
        processing_scenarios: Union[Callable, Sequence[Callable]],
) -> ProcessingResults:
    """Process a single simulation folder using the provided processing scenario(s).

    Args:
        sim_folder: Path to the simulation folder to process
        processing_scenarios: Single callable or sequence of callables that implement
            the processing logic for a simulation. Each callable should take a Simulation
            object as its only parameter.

    Returns:
        ProcessingResults containing the processed simulation and any failures

    Example:
        >>> import pathlib as _pl
        >>> from pytrnsys_process import api
        ...
        >>> def processing_step_1(sim: api.Simulation):
        ...     # Process simulation data
        ...     pass
        >>> results = api.process_single_simulation(
        ...     _pl.Path("path/to/simulation"),
        ...     processing_step_1
        ... )
        >>> print(f"Processed: {results.processed_count}")
    """
    results = ProcessingResults()
    try:
        simulation, failed_scenarios = _process_simulation(
            sim_folder, processing_scenarios
        )
        results.processed_count += 1
        results.simulations[simulation.path.name] = simulation
        if failed_scenarios:
            results.failed_scenarios[simulation.path.name] = failed_scenarios
    except Exception as e:  # pylint: disable=broad-except
        results.error_count += 1
        results.failed_simulations.append(sim_folder.name)
        logger.error(
            "Failed to process simulation in %s: %s",
            sim_folder,
            str(e),
            exc_info=True,
        )
    return results


def process_whole_result_set(
        results_folder: _pl.Path,
        processing_scenario: Union[Callable, Sequence[Callable]],
) -> ProcessingResults:
    """Process all simulation folders in a results directory sequentially.

    Args:
        results_folder: Path to the directory containing simulation folders
        processing_scenario: Single callable or sequence of callables that implement
            the processing logic for each simulation. Each callable should take a
            Simulation object as its only parameter.

    Returns:
        ProcessingResults containing counts of processed and failed simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory

    Example:
        >>> import pathlib as _pl
        >>> from pytrnsys_process import api
        ...
        >>> def processing_step_1(sim):
        ...     # Process simulation data
        ...     pass
        >>> def processing_step_2(sim):
        ...     # Process simulation data
        ...     pass
        >>> results = api.process_whole_result_set(
        ...     _pl.Path("path/to/results"),
        ...     [processing_step_1, processing_step_2]
        ... )
        >>> print(f"Processed: {results.processed_count}, Failed: {results.error_count}")
    """
    _validate_folder(results_folder)

    logger.info(
        "Starting batch processing of simulations in %s", results_folder
    )
    results = ProcessingResults()

    for sim_folder in results_folder.iterdir():
        if not sim_folder.is_dir():
            continue

        try:
            simulation, failed_scenarios = _process_simulation(
                sim_folder, processing_scenario
            )
            results.processed_count += 1
            results.simulations[simulation.path.name] = simulation
            if failed_scenarios:
                results.failed_scenarios[simulation.path.name] = (
                    failed_scenarios
                )
        except Exception as e:  # pylint: disable=broad-except
            results.error_count += 1
            results.failed_simulations.append(sim_folder.name)
            logger.error(
                "Failed to process simulation in %s: %s",
                sim_folder,
                str(e),
                exc_info=True,
            )

    all_decks = [sim.deck for sim in results.simulations.values()]
    results.decks = _pd.concat(all_decks)

    _log_processing_results(results)
    return results


def process_whole_result_set_parallel(
    results_folder: _pl.Path,
        processing_scenario: Union[Callable, Sequence[Callable]],
    max_workers: int | None = None,
) -> ProcessingResults:
    """Process all simulation folders in a results directory in parallel.

    Uses a ProcessPoolExecutor to process multiple simulations concurrently.

    Args:
        results_folder: Path to the directory containing simulation folders
        processing_scenario: Single callable or sequence of callables that implement
            the processing logic for each simulation. Each callable should take a
            Simulation object as its only parameter.
        max_workers: Maximum number of worker processes to use. If None, defaults to
            the number of processors on the machine.

    Returns:
        ProcessingResults containing counts of processed and failed simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory

    Example:
        >>> import pathlib as _pl
        >>> from pytrnsys_process import api
        ...
        >>> def processing_step_1(sim):
        ...     # Process simulation data
        ...     pass
        >>> def processing_step_2(sim):
        ...     # Process simulation data
        ...     pass
        >>> results = api.process_whole_result_set_parallel(
        ...     _pl.Path("path/to/results"),
        ...     [processing_step_1, processing_step_2]
        ... )
        >>> print(f"Processed: {results.processed_count}, Failed: {results.error_count}")
    """
    _validate_folder(results_folder)

    logger.info(
        "Starting batch processing of simulations in %s with parallel execution",
        results_folder,
    )
    results = ProcessingResults()

    sim_folders = [
        sim_folder
        for sim_folder in results_folder.iterdir()
        if sim_folder.is_dir()
    ]

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        tasks = {
            executor.submit(
                _process_simulation, sim_folder, processing_scenario
            ): sim_folder
            for sim_folder in sim_folders
        }

        for future in as_completed(tasks):
            try:
                simulation, failed_scenarios = future.result()
                results.processed_count += 1
                results.simulations[simulation.path.name] = simulation
                if failed_scenarios:
                    results.failed_scenarios[simulation.path.name] = (
                        failed_scenarios
                    )
            except Exception as e:  # pylint: disable=broad-except
                results.error_count += 1
                results.failed_simulations.append(tasks[future].name)
                logger.error(
                    "Failed to process simulation in %s: %s",
                    tasks[future].name,
                    str(e),
                    exc_info=True,
                )

    _log_processing_results(results)
    return results

# def do_comparison(simulations: list[Simulation], comparison_scenario: Union[Callable, Sequence[Callable]]):
