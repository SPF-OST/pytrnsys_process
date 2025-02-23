import pathlib as _pl
import time as _time
from collections import abc as _abc
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Sequence, Union

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import constants as const
from pytrnsys_process import data_structures as ds
from pytrnsys_process import logger as log
from pytrnsys_process import settings as sett
from pytrnsys_process import utils
from pytrnsys_process.process_sim import process_sim as ps


class UnableToProcessSimulationError(Exception):
    """Raised when a simulation cannot be processed."""


# pylint: disable=too-many-locals
def _process_batch(
        sim_folders: list[_pl.Path],
        processing_scenario: Union[
            _abc.Callable[[ds.Simulation], None],
            Sequence[_abc.Callable[[ds.Simulation], None]],
        ],
        results_folder: _pl.Path,
        parallel: bool = False,
        max_workers: int | None = None,
) -> ds.SimulationsData:
    """Common processing logic for both sequential and parallel batch processing.

    This internal function implements the core processing logic used by both sequential
    and parallel processing modes. It handles the setup of processing infrastructure,
    execution of processing tasks, and collection of results.

    Args:
        sim_folders: List of simulation folders to process
        processing_scenario: Processing scenario(s) to apply to each simulation
        results_folder: Root folder containing all simulations
        parallel: Whether to process simulations in parallel
        max_workers: Maximum number of worker processes for parallel execution

    Returns:
        SimulationsData containing the processed simulation results and metadata

    Note:
        This is an internal function that should not be called directly.
        Use process_single_simulation, process_whole_result_set, or
        process_whole_result_set_parallel instead.
    """
    start_time = _time.time()
    results = ds.ProcessingResults()
    simulations_data = ds.SimulationsData(path_to_simulations=results_folder)

    if parallel:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            tasks = {}
            for sim_folder in sim_folders:
                log.main_logger.info(
                    "Submitting simulation folder for processing: %s",
                    sim_folder.name,
                )
                tasks[
                    executor.submit(
                        _process_simulation, sim_folder, processing_scenario
                    )
                ] = sim_folder

            for future in as_completed(tasks):
                try:
                    _handle_simulation_result(
                        future.result(), results, simulations_data
                    )
                except Exception as e:  # pylint: disable=broad-except
                    _handle_simulation_error(e, tasks[future], results)
    else:
        for sim_folder in sim_folders:
            try:
                log.main_logger.info(
                    "Processing simulation: %s", sim_folder.name
                )
                result = _process_simulation(sim_folder, processing_scenario)
                _handle_simulation_result(result, results, simulations_data)
            except Exception as e:  # pylint: disable=broad-except
                _handle_simulation_error(e, sim_folder, results)

    simulations_data = _concat_scalar(simulations_data)
    _log_processing_results(results)

    end_time = _time.time()
    execution_time = end_time - start_time
    log.main_logger.info(
        "%s execution time: %.2f seconds",
        "Parallel" if parallel else "Total",
        execution_time,
    )

    return simulations_data


def _handle_simulation_result(
        result: tuple[ds.Simulation, List[str]],
        results: ds.ProcessingResults,
        simulations_data: ds.SimulationsData,
) -> None:
    """Handle the result of a processed simulation.

    Args:
        result: Tuple of (simulation, failed_scenarios)
        sim_folder: Path to the simulation folder
        results: ProcessingResults to update
        simulations_data: SimulationsData to update
    """
    simulation, failed_scenarios = result
    results.processed_count += 1
    simulations_data.simulations[simulation.path.name] = simulation
    if failed_scenarios:
        results.failed_scenarios[simulation.path.name] = failed_scenarios


def _handle_simulation_error(
        error: Exception,
        sim_folder: _pl.Path,
        results: ds.ProcessingResults,
) -> None:
    """Handle an error that occurred during simulation processing.

    Args:
        error: The exception that occurred
        sim_folder: Path to the simulation folder
        results: ProcessingResults to update
    """
    results.error_count += 1
    results.failed_simulations.append(sim_folder.name)
    log.main_logger.error(
        "Failed to process simulation in %s: %s",
        sim_folder,
        str(error),
        exc_info=True,
    )


def process_single_simulation(
        sim_folder: _pl.Path,
        processing_scenarios: Union[
            _abc.Callable[[ds.Simulation], None],
            Sequence[_abc.Callable[[ds.Simulation], None]],
        ],
) -> ds.Simulation:
    """Process a single simulation folder using the provided processing scenario(s).

        Args:
            sim_folder: Path to the simulation folder to process
            processing_scenarios: Single callable or sequence of callables that implement
                the processing logic for a simulation. Each callable should take a Simulation
                object as its only parameter.

        Returns:
            Simulation object containing the processed data

        Example:
    import data_structures        >>> import pathlib as _pl
            >>> from pytrnsys_process import api
            ...
            >>> def processing_step_1(sim: data_structures.Simulation):
            ...     # Process simulation data
            ...     pass
            >>> results = api.process_single_simulation(
            ...     _pl.Path("path/to/simulation"),
            ...     processing_step_1
            ... )
            >>> api.compare_results(results, comparison_step_1)
    """
    log.initialize_logs()
    log.main_logger.info("Starting processing of simulation %s", sim_folder)
    sim_folders = [sim_folder]
    simulations_data = _process_batch(
        sim_folders, processing_scenarios, sim_folder.parent
    )
    try:
        return simulations_data.simulations[sim_folder.name]
    except KeyError as exc:
        raise UnableToProcessSimulationError(
            f"Failed to process simulation in {sim_folder}"
        ) from exc


def process_whole_result_set(
        results_folder: _pl.Path,
        processing_scenario: Union[
            _abc.Callable[[ds.Simulation], None],
            Sequence[_abc.Callable[[ds.Simulation], None]],
        ],
) -> ds.SimulationsData:
    """Process all simulation folders in a results directory sequentially.

    Processes each simulation folder found in the results directory one at a time,
    applying the provided processing scenario(s) to each simulation.

    Args:
        results_folder: Path to the directory containing simulation folders.
            Each subfolder should contain valid simulation data files.
        processing_scenario: Single callable or sequence of callables that implement
            the processing logic for each simulation. Each callable should take a
            Simulation object as its only parameter and modify it in place.

    Returns:
        ResultsForComparison object containing:
            - monthly: Dict mapping simulation names to monthly DataFrame results
            - hourly: Dict mapping simulation names to hourly DataFrame results
            - scalar: DataFrame containing scalar/deck values from all simulations
        ProcessingResults containing counts of processed and failed simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory
        Exception: Individual simulation failures are logged but not re-raised

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
        >>> api.compare_results(results, comparison_step_1)
    """
    _validate_folder(results_folder)
    log.initialize_logs()
    log.main_logger.info(
        "Starting batch processing of simulations in %s", results_folder
    )

    sim_folders = [
        sim_folder
        for sim_folder in results_folder.iterdir()
        if sim_folder.is_dir()
    ]
    simulations_data = _process_batch(
        sim_folders, processing_scenario, results_folder
    )
    utils.save_to_pickle(
        simulations_data,
        results_folder / const.FileNames.SIMULATIONS_DATA_PICKLE_FILE.value,
    )

    return simulations_data


def process_whole_result_set_parallel(
    results_folder: _pl.Path,
        processing_scenario: Union[
            _abc.Callable[[ds.Simulation], None],
            Sequence[_abc.Callable[[ds.Simulation], None]],
        ],
    max_workers: int | None = None,
) -> ds.SimulationsData:
    """Process all simulation folders in a results directory in parallel.

    Uses a ProcessPoolExecutor to process multiple simulations concurrently.

    Args:
        results_folder: Path to the directory containing simulation folders.
            Each subfolder should contain valid simulation data files.
        processing_scenario: Single callable or sequence of callables that implement
            the processing logic for each simulation. Each callable should take a
            Simulation object as its only parameter.
        max_workers: Maximum number of worker processes to use. If None, defaults to
            the number of processors on the machine.

    Returns:
        ResultsForComparison object containing:
            - monthly: Dict mapping simulation names to monthly DataFrame results
            - hourly: Dict mapping simulation names to hourly DataFrame results
            - scalar: DataFrame containing scalar/deck values from all simulations

    Raises:
        ValueError: If results_folder doesn't exist or is not a directory
        Exception: Individual simulation failures are logged but not re-raised

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
        >>> api.compare_results(results, comparison_step_1)
    """
    _validate_folder(results_folder)
    log.initialize_logs()
    log.main_logger.info(
        "Starting batch processing of simulations in %s with parallel execution",
        results_folder,
    )

    sim_folders = [
        sim_folder
        for sim_folder in results_folder.iterdir()
        if sim_folder.is_dir()
    ]
    simulations_data = _process_batch(
        sim_folders,
        processing_scenario,
        results_folder,
        parallel=True,
        max_workers=max_workers,
    )
    utils.save_to_pickle(
        simulations_data,
        results_folder / const.FileNames.SIMULATIONS_DATA_PICKLE_FILE.value,
    )

    return simulations_data


def do_comparison(
        simulations_data: ds.SimulationsData,
        comparison_scenario: Union[
            _abc.Callable[[ds.SimulationsData], None],
            _abc.Sequence[_abc.Callable[[ds.SimulationsData], None]],
        ],
):
    """Execute comparison scenarios on processed simulation results.

        Args:
            results_for_comparison: ResultsForComparison object containing the processed
                simulation data to be compared
            comparison_scenario: Single callable or sequence of callables that implement
                the comparison logic. Each callable should take a ResultsForComparison
                object as its only parameter.

        Example:
    import data_structures        >>> from pytrnsys_process import api
            ...
            >>> def comparison_step(comparison_results: data_structures.ResultsForComparison):
            ...     # Compare simulation results
            ...     pass
            ...
            >>> api.do_comparison(processed_results, comparison_step)
    """
    try:
        _process_comparisons(simulations_data, comparison_scenario)
        _plt.close("all")
    except Exception:  # pylint: disable=broad-except
        log.main_logger.error(
            "Failed to do comparison",
            exc_info=True,
        )


def _process_comparisons(
        simulations_data: ds.SimulationsData,
        comparison_scenario: Union[
            _abc.Callable[[ds.SimulationsData], None],
            _abc.Sequence[_abc.Callable[[ds.SimulationsData], None]],
        ],
):
    scenario = (
        [comparison_scenario]
        if callable(comparison_scenario)
        else comparison_scenario
    )
    for step in scenario:
        try:
            step(simulations_data)
        except Exception as e:  # pylint: disable=broad-except
            scenario_name = getattr(step, "__name__", str(step))
            log.main_logger.error(
                "Scenario %s failed for comparison: %s ",
                scenario_name,
                str(e),
                exc_info=True,
            )


def _concat_scalar(simulation_data: ds.SimulationsData) -> ds.SimulationsData:
    scalar_values_to_concat = {
        sim_name: sim.scalar
        for sim_name, sim in simulation_data.simulations.items()
        if not sim.scalar.empty
    }
    if scalar_values_to_concat:
        simulation_data.scalar = _pd.concat(
            scalar_values_to_concat.values(),
            keys=scalar_values_to_concat.keys(),
        ).droplevel(1)
    return simulation_data


def _validate_folder(folder: _pl.Path) -> None:
    if not folder.exists():
        raise ValueError(f"Folder does not exist: {folder}")
    if not folder.is_dir():
        raise ValueError(f"Path is not a directory: {folder}")


def _process_simulation(
        sim_folder: _pl.Path,
        processing_scenarios: Union[
            _abc.Callable[[ds.Simulation], None],
            Sequence[_abc.Callable[[ds.Simulation], None]],
        ],
) -> tuple[ds.Simulation, List[str]]:
    sim_logger = log.get_simulation_logger(sim_folder)
    sim_logger.info("Starting simulation processing")
    sim_pickle_file = sim_folder / const.FileNames.SIMULATION_PICKLE_FILE.value
    simulation: ds.Simulation
    if sim_pickle_file.exists() and not sett.settings.reader.force_reread_prt:
        sim_logger.info("Loading simulation from pickle file")
        simulation = utils.load_simulation_from_pickle(
            sim_pickle_file, sim_logger
        )
    else:
        sim_logger.info("Processing simulation from raw files")
        sim_files = utils.get_files([sim_folder])
        simulation = ps.process_sim(sim_files, sim_folder)
        utils.save_to_pickle(simulation, sim_pickle_file, sim_logger)

    failed_scenarios = []

    # Convert single scenario to list for uniform handling
    scenarios = (
        [processing_scenarios]
        if callable(processing_scenarios)
        else processing_scenarios
    )

    for scenario in scenarios:
        try:
            scenario_name = getattr(scenario, "__name__", str(scenario))
            sim_logger.info("Running scenario: %s", scenario_name)
            scenario(simulation)
            sim_logger.info(
                "Successfully completed scenario: %s", scenario_name
            )
        except Exception as e:  # pylint: disable=broad-except
            failed_scenarios.append(scenario_name)
            sim_logger.error(
                "Scenario %s failed: %s",
                scenario_name,
                str(e),
                exc_info=True,
            )

    if failed_scenarios:
        sim_logger.warning(
            "Simulation completed with %d failed scenarios",
            len(failed_scenarios),
        )
    else:
        sim_logger.info("Simulation completed successfully")

    _plt.close("all")
    return simulation, failed_scenarios


def _log_processing_results(results: ds.ProcessingResults) -> None:
    log.main_logger.info("=" * 80)
    log.main_logger.info("BATCH PROCESSING SUMMARY")
    log.main_logger.info("-" * 80)
    log.main_logger.info(
        "Total simulations processed: %d | Failed: %d",
        results.processed_count,
        results.error_count,
    )

    if results.error_count > 0:
        log.main_logger.warning(
            "Some simulations failed to process. Check the log for details."
        )
        log.main_logger.warning("Failed simulations:")
        for sim in results.failed_simulations:
            log.main_logger.warning("  • %s", sim)

    if results.failed_scenarios:
        log.main_logger.warning("Failed scenarios by simulation:")
        for sim, scenarios in results.failed_scenarios.items():
            if scenarios:
                log.main_logger.warning("  • %s:", sim)
                for scenario in scenarios:
                    log.main_logger.warning("    - %s", scenario)
    log.main_logger.info("=" * 80)
