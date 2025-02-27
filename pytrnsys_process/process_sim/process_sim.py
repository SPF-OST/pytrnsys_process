import logging as _logging
import pathlib as _pl
from collections import abc as _abc
from dataclasses import dataclass, field

import pandas as _pd

from pytrnsys_process import constants as const
from pytrnsys_process import data_structures as ds
from pytrnsys_process import file_type_detector as ftd
from pytrnsys_process import logger as log
from pytrnsys_process import readers
from pytrnsys_process import settings as sett
from pytrnsys_process import utils
from pytrnsys_process.deck import extractor
from pytrnsys_process.settings import settings


def process_sim(
    sim_files: _abc.Sequence[_pl.Path], sim_folder: _pl.Path
) -> ds.Simulation:
    # Used to store the array of dataframes for each file type.
    # Later used to concatenate all into one dataframe and saving as Sim object
    simulation_data_collector = _SimulationDataCollector()

    sim_logger = log.get_simulation_logger(sim_folder)
    for sim_file in sim_files:
        try:
            _process_file(
                simulation_data_collector,
                sim_file,
                _determine_file_type(sim_file, sim_logger),
            )
        except ValueError as e:
            sim_logger.error(
                "Error reading file %s it will not be available for processing: %s",
                sim_file,
                str(e),
                exc_info=True,
            )

    return _merge_dataframes_into_simulation(
        simulation_data_collector, sim_folder
    )


def handle_duplicate_columns(df: _pd.DataFrame) -> _pd.DataFrame:
    """
    Process duplicate columns in a DataFrame, ensuring they contain consistent data.

    This function checks for duplicate column names and verifies that:
    1. If one duplicate column has NaN values, the other(s) must also have NaN at the same indices
    2. All non-NaN values must be identical across duplicate columns

    Parameters
    __________
    df: pandas.DataFrame
        Input DataFrame to process

    Returns
    _______
    df: pandas.DataFrame
        DataFrame with duplicate columns removed, keeping only the first occurrence

    Raises
    ______
    ValueError
        If duplicate columns have:
        1. NaN values in one column while having actual values in another at the same index, or
        2. Different non-NaN values at the same index

    Note
    ____
    https://stackoverflow.com/questions/14984119/python-pandas-remove-duplicate-columns
    """
    for col in df.columns[df.columns.duplicated(keep=False)]:
        duplicate_cols = df.iloc[:, df.columns == col]

        nan_mask = duplicate_cols.isna()
        value_mask = ~nan_mask
        if ((nan_mask.sum(axis=1) > 0) & (value_mask.sum(axis=1) > 0)).any():
            raise ValueError(
                f"Column '{col}' has NaN values in one column while having actual values in another"
            )

        if not duplicate_cols.apply(lambda x: x.nunique() <= 1, axis=1).all():
            raise ValueError(
                f"Column '{col}' has conflicting values at same indices"
            )

    df = df.iloc[:, ~df.columns.duplicated()].copy()
    return df


def _determine_file_type(
    sim_file: _pl.Path, logger: _logging.Logger
) -> const.FileType:
    """Determine the file type using name and content."""
    try:
        return ftd.get_file_type_using_file_name(sim_file, logger)
    except ValueError:
        return ftd.get_file_type_using_file_content(sim_file, logger)


@dataclass
class _SimulationDataCollector:
    hourly: list[_pd.DataFrame] = field(default_factory=list)
    monthly: list[_pd.DataFrame] = field(default_factory=list)
    step: list[_pd.DataFrame] = field(default_factory=list)
    deck: _pd.DataFrame = field(default_factory=_pd.DataFrame)


def _read_file(
    file_path: _pl.Path, file_type: const.FileType
) -> _pd.DataFrame:
    """
    Factory method to read data from a file using the appropriate reader.

    Parameters
    __________
    file_path: pathlib.Path
        Path to the file to be read

    file_type: const.FileType
        Type of data in the file (MONTHLY, HOURLY, or TIMESTEP)

    Returns
    _______
    pandas.DataFrame
        Data read from the file

    Raises
    ______
    ValueError
        If file extension is not supported
    """
    starting_year = settings.reader.starting_year
    extension = file_path.suffix.lower()
    if extension in [".prt", ".hr"]:
        reader = readers.PrtReader()
        if file_type == const.FileType.MONTHLY:
            return reader.read_monthly(file_path, starting_year)
        if file_type == const.FileType.HOURLY:
            return reader.read_hourly(file_path, starting_year)
        if file_type == const.FileType.TIMESTEP:
            return reader.read_step(file_path, starting_year)
    elif extension == ".csv":
        return readers.CsvReader().read_csv(file_path)

    raise ValueError(f"Unsupported file extension: {extension}")


def _process_file(
    simulation_data_collector: _SimulationDataCollector,
    file_path: _pl.Path,
    file_type: const.FileType,
) -> bool:
    if file_type == const.FileType.MONTHLY:
        simulation_data_collector.monthly.append(
            _read_file(file_path, const.FileType.MONTHLY)
        )
    elif file_type == const.FileType.HOURLY:
        simulation_data_collector.hourly.append(
            _read_file(file_path, const.FileType.HOURLY)
        )
    elif (
        file_type == const.FileType.TIMESTEP
        and sett.settings.reader.read_step_files
    ):
        simulation_data_collector.step.append(
            _read_file(file_path, const.FileType.TIMESTEP)
        )
    elif (
        file_type == const.FileType.DECK
        and sett.settings.reader.read_deck_files
    ):
        simulation_data_collector.deck = _get_deck_as_df(file_path)
    else:
        return False
    return True


def _get_deck_as_df(
    file_path: _pl.Path,
) -> _pd.DataFrame:
    deck_file_as_string = utils.get_file_content_as_string(file_path)
    deck: dict[str, float] = extractor.parse_deck_for_constant_expressions(
        deck_file_as_string, log.get_simulation_logger(file_path.parent)
    )
    deck_as_df = _pd.DataFrame([deck])
    return deck_as_df


def _merge_dataframes_into_simulation(
    simulation_data_collector: _SimulationDataCollector, sim_folder: _pl.Path
) -> ds.Simulation:
    monthly_df = _get_df_without_duplicates(simulation_data_collector.monthly)
    hourly_df = _get_df_without_duplicates(simulation_data_collector.hourly)
    timestep_df = _get_df_without_duplicates(simulation_data_collector.step)
    deck = simulation_data_collector.deck

    return ds.Simulation(
        sim_folder.as_posix(), monthly_df, hourly_df, timestep_df, deck
    )


def _get_df_without_duplicates(dfs: _abc.Sequence[_pd.DataFrame]):
    if len(dfs) > 0:
        return handle_duplicate_columns(_pd.concat(dfs, axis=1))

    return _pd.DataFrame()
