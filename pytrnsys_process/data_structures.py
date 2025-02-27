from dataclasses import dataclass, field
from typing import List

import pandas as _pd


@dataclass
class Simulation:
    """Class representing a TRNSYS simulation with its associated data.

    This class holds the simulation data organized in different time resolutions (monthly, hourly, timestep)
    along with the path to the simulation files.

    Attributes
    __________
    path: str
        Path to the simulation folder containing the input files

    monthly: pandas.DataFrame
        Monthly aggregated simulation data. Each column represents a different variable
        and each row represents a month.

    hourly: pandas.DataFrame
        Hourly simulation data. Each column represents a different variable
        and each row represents an hour.

    step: pandas.DataFrame
        Simulation data at the smallest timestep resolution. Each column represents
        a different variable and each row represents a timestep.
    """

    path: str
    monthly: _pd.DataFrame
    hourly: _pd.DataFrame
    step: _pd.DataFrame
    scalar: _pd.DataFrame


@dataclass
class ProcessingResults:
    """Results from processing one or more simulations.

    Attributes
    __________
    processed_count:
            Number of successfully processed simulations

    error_count:
        Number of simulations that failed to process

    failed_simulations:
        List of simulation names that failed to process

    failed_scenarios:
        Dictionary mapping simulation names to lists of failed scenario names

    simulations:
        Dictionary mapping simulation names to processed Simulation objects

    Example
    _______
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


@dataclass
class SimulationsData:
    simulations: dict[str, Simulation] = field(default_factory=dict)
    scalar: _pd.DataFrame = field(default_factory=_pd.DataFrame)
    path_to_simulations: str = field(default_factory=str)
