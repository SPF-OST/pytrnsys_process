import pathlib as _pl
from collections import abc as _abc
from dataclasses import dataclass, field

import pandas as _pd

from pytrnsys_process import constants as const
from pytrnsys_process import file_type_detector as ftd
from pytrnsys_process import readers
from pytrnsys_process import settings as sett
from pytrnsys_process.logger import logger


@dataclass
class Simulation:
    """Class representing a TRNSYS simulation with its associated data.

    This class holds the simulation data organized in different time resolutions (monthly, hourly, timestep)
    along with the path to the simulation files.

    Attributes
    ----------
    path : pathlib.Path
        Path to the simulation folder containing the input files
    monthly : pandas.DataFrame
        Monthly aggregated simulation data. Each column represents a different variable
        and each row represents a month.
    hourly : pandas.DataFrame
        Hourly simulation data. Each column represents a different variable
        and each row represents an hour.
    step : pandas.DataFrame
        Simulation data at the smallest timestep resolution. Each column represents
        a different variable and each row represents a timestep.
    """

    path: _pl.Path
    monthly: _pd.DataFrame
    hourly: _pd.DataFrame
    step: _pd.DataFrame
    # TODO: Add results data here. Not sure yet, what this will look like # pylint: disable=fixme


def process_sim(
        sim_files: _abc.Sequence[_pl.Path], sim_folder: _pl.Path
) -> Simulation:
    # Used to store the array of dataframes for each file type.
    # Later used to concatenate all into one dataframe and saving as Sim object
    simulation_data_collector = _SimulationDataCollector()
    for sim_file in sim_files:
        try:
            _process_file(
                simulation_data_collector,
                sim_file,
                _determine_file_type(sim_file),
            )
        except ValueError as e:
            logger.error(
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
    ----------
    df : pandas.DataFrame
        Input DataFrame to process

    Returns
    -------
    pandas.DataFrame
        DataFrame with duplicate columns removed, keeping only the first occurrence

    Raises
    ------
    ValueError
        If duplicate columns have:
        - NaN values in one column while having actual values in another at the same index
        - Different non-NaN values at the same index

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


def _determine_file_type(sim_file: _pl.Path) -> const.FileType:
    """Determine the file type using name and content."""
    try:
        return ftd.get_file_type_using_file_name(sim_file)
    except ValueError:
        return ftd.get_file_type_using_file_content(sim_file)


@dataclass
class _SimulationDataCollector:
    hourly: list[_pd.DataFrame] = field(default_factory=list)
    monthly: list[_pd.DataFrame] = field(default_factory=list)
    step: list[_pd.DataFrame] = field(default_factory=list)


def _read_file(
        file_path: _pl.Path, file_type: const.FileType
) -> _pd.DataFrame:
    """
    Factory method to read data from a file using the appropriate reader.

    Parameters
    ----------
    file_path : pathlib.Path
        Path to the file to be read
    file_type : const.FileType
        Type of data in the file (MONTHLY, HOURLY, or TIMESTEP)

    Returns
    -------
    pandas.DataFrame
        Data read from the file

    Raises
    ------
    ValueError
        If file extension is not supported
    """
    extension = file_path.suffix.lower()
    if extension in [".prt", ".hr"]:
        reader = readers.PrtReader()
        if file_type == const.FileType.MONTHLY:
            return reader.read_monthly(file_path)
        if file_type == const.FileType.HOURLY:
            return reader.read_hourly(file_path)
        if file_type == const.FileType.TIMESTEP:
            return reader.read_step(file_path)
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
    else:
        return False

    return True


def _merge_dataframes_into_simulation(
        simulation_data_collector: _SimulationDataCollector, sim_folder: _pl.Path
) -> Simulation:

    monthly_df = get_df_without_duplicates(simulation_data_collector.monthly)
    hourly_df = get_df_without_duplicates(simulation_data_collector.hourly)
    timestep_df = get_df_without_duplicates(simulation_data_collector.step)

    return Simulation(sim_folder, monthly_df, hourly_df, timestep_df)


def get_df_without_duplicates(dfs: _abc.Sequence[_pd.DataFrame]):
    if len(dfs) > 0:
        return handle_duplicate_columns(_pd.concat(dfs, axis=1))

    return _pd.DataFrame()
