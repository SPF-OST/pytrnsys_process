import pathlib as _pl
from dataclasses import dataclass

import pandas as _pd

from pytrnsys_process import file_matcher as fm
from pytrnsys_process import readers, utils
from pytrnsys_process.logger import logger


# TODO test if overlapping colums are allowed if the value are the same # pylint: disable=fixme


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


def process_sim_prt(
    sim_folder: _pl.Path,
) -> Simulation:
    sim_files = utils.get_files([sim_folder])
    prt_reader = readers.PrtReader()
    hourly = []
    monthly = []
    timestep = []

    for sim_file in sim_files:
        if fm.has_pattern(sim_file.name, fm.FileType.MONTHLY):
            monthly.append(prt_reader.read_monthly(sim_file))
        elif fm.has_pattern(sim_file.name, fm.FileType.HOURLY):
            hourly.append(prt_reader.read_hourly(sim_file))
        elif fm.has_pattern(sim_file.name, fm.FileType.TIMESTEP):
            timestep.append(prt_reader.read_step(sim_file))
        else:
            logger.warning("Unknown file type: %s", sim_file.name)

    monthly_df = (
        handle_duplicate_columns(_pd.concat(monthly, axis=1))
        if monthly
        else _pd.DataFrame()
    )
    hourly_df = (
        handle_duplicate_columns(_pd.concat(hourly, axis=1))
        if hourly
        else _pd.DataFrame()
    )
    timestep_df = (
        handle_duplicate_columns(_pd.concat(timestep, axis=1))
        if timestep
        else _pd.DataFrame()
    )
    return Simulation(sim_folder, monthly_df, hourly_df, timestep_df)


def process_sim_using_file_content_prt(
    sim_folder: _pl.Path,
) -> Simulation:
    sim_files = utils.get_files([sim_folder])
    prt_reader = readers.PrtReader()
    hourly = []
    monthly = []
    step = []

    for sim_file in sim_files:
        file_type = fm.get_file_type_using_file_content(sim_file)
        if file_type == fm.FileType.MONTHLY:
            monthly.append(prt_reader.read_monthly(sim_file))
        elif file_type == fm.FileType.HOURLY:
            hourly.append(prt_reader.read_hourly(sim_file))
        elif file_type == fm.FileType.TIMESTEP:
            step.append(prt_reader.read_step(sim_file))
        else:
            logger.warning("Unknown file type: %s", sim_file.name)

    monthly_df = handle_duplicate_columns(_pd.concat(monthly, axis=1))
    hourly_df = handle_duplicate_columns(_pd.concat(hourly, axis=1))
    timestep_df = handle_duplicate_columns(_pd.concat(step, axis=1))
    return Simulation(sim_folder, monthly_df, hourly_df, timestep_df)


def process_sim_csv(
    sim_folder: _pl.Path,
) -> Simulation:
    sim_files = utils.get_files([sim_folder], results_folder_name="converted")
    csv_reader = readers.CsvReader()
    hourly = []
    monthly = []
    timestep = []

    for sim_file in sim_files:
        if fm.has_pattern(sim_file.name, fm.FileType.MONTHLY):
            monthly.append(csv_reader.read_csv(sim_file))
        elif fm.has_pattern(sim_file.name, fm.FileType.HOURLY):
            hourly.append(csv_reader.read_csv(sim_file))
        elif fm.has_pattern(sim_file.name, fm.FileType.TIMESTEP):
            timestep.append(csv_reader.read_csv(sim_file))
        else:
            logger.warning("Unknown file type: %s", sim_file.name)

    monthly_df = handle_duplicate_columns(_pd.concat(monthly, axis=1))
    hourly_df = handle_duplicate_columns(_pd.concat(hourly, axis=1))
    timestep_df = handle_duplicate_columns(_pd.concat(timestep, axis=1))

    return Simulation(sim_folder, monthly_df, hourly_df, timestep_df)
