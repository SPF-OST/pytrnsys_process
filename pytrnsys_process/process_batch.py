import pathlib as _pl
from collections.abc import Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List

import matplotlib.pyplot as _plt

from pytrnsys_process.logger import logger
from pytrnsys_process.process_sim import process_sim as ps


@dataclass
class ProcessingResults:
    """Results from processing one or more simulations"""

    processed_count: int = 0
    error_count: int = 0
    failed_simulations: List[str] = field(default_factory=list)
    simulations: dict[str, ps.Simulation] = field(default_factory=dict)


def _validate_folder(folder: _pl.Path) -> None:
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")


def _process_simulation(
    sim_folder: _pl.Path, processing_scenario: Callable
) -> ps.Simulation:
    logger.debug("Processing simulation folder: %s", sim_folder)
    simulation = ps.process_sim_prt(sim_folder)
    processing_scenario(simulation)
    _plt.close("all")
    return simulation


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


def process_single_simulation(
    sim_folder: _pl.Path, processing_scenario: Callable
) -> ProcessingResults:
    """Process a single simulation folder using the provided processing scenario.

    Args:
        sim_folder: Path to the simulation folder to process
        processing_scenario: Callable that implements the processing logic for a simulation

    Returns:
        ProcessingResults containing the processed simulation

    Raises:
        Exception: If processing fails. The error will be logged but not re-raised.
    """
    results = ProcessingResults()
    try:
        simulation = _process_simulation(sim_folder, processing_scenario)
        results.processed_count += 1
        results.simulations[simulation.path.name] = simulation
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
    results_folder: _pl.Path, processing_scenario: Callable
) -> ProcessingResults:
    """Process all simulation folders in a results directory sequentially.

    Args:
        results_folder: Path to the directory containing simulation folders
        processing_scenario: Callable that implements the processing logic for each simulation

    Returns:
        ProcessingResults containing counts of processed and failed simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory
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
            simulation = _process_simulation(sim_folder, processing_scenario)
            results.processed_count += 1
            results.simulations[simulation.path.name] = simulation
        except Exception as e:  # pylint: disable=broad-except
            results.error_count += 1
            results.failed_simulations.append(sim_folder.name)
            logger.error(
                "Failed to process simulation in %s: %s",
                sim_folder,
                str(e),
                exc_info=True,
            )

    _log_processing_results(results)
    return results


def process_whole_result_set_parallel(
    results_folder: _pl.Path,
    processing_scenario: Callable,
    max_workers: int | None = None,
) -> ProcessingResults:
    """Process all simulation folders in a results directory in parallel.

    Uses a ProcessPoolExecutor to process multiple simulations concurrently.

    Args:
        results_folder: Path to the directory containing simulation folders
        processing_scenario: Callable that implements the processing logic for each simulation
        max_workers: Maximum number of worker processes to use. If None, defaults to the number
            of processors on the machine.

    Returns:
        ProcessingResults containing counts of processed and failed simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory
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
                simulation = future.result()
                results.processed_count += 1
                results.simulations[simulation.path.name] = simulation
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
