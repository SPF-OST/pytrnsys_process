import datetime as _dt
import pathlib as _pl

from pytrnsys_process import constants as const
from pytrnsys_process import readers
from pytrnsys_process.logger import logger


def get_file_type_using_file_content(file_path: _pl.Path) -> const.FileType:
    """
    Determine the file type by analyzing its content.

    Args:
        file_path (Path): Path to the file to analyze

    Returns:
        FileType: The detected file type (MONTHLY, HOURLY, or TIMESTEP)
    """
    reader = readers.PrtReader()

    # First try reading as regular file to check if it's monthly
    df = reader.read(file_path)
    if df.columns[0] == "Month":
        logger.info("Detected %s as monthly file", file_path)
        return const.FileType.MONTHLY

    # If not monthly, read as step and check time interval
    df_step_or_hourly = reader.read_step(file_path)
    time_interval = df_step_or_hourly.index[1] - df_step_or_hourly.index[0]

    if time_interval < _dt.timedelta(hours=1):
        logger.info("Detected %s as step file", file_path)
        return const.FileType.TIMESTEP

    logger.info("Detected %s as hourly file", file_path)
    return const.FileType.HOURLY


def get_file_type_using_file_name(file_name: str) -> const.FileType:
    """
    Determine the file type by checking the filename against known patterns.

    Args:
        file_name (str): The name of the file to check

    Returns:
        FileType: The detected file type (MONTHLY, HOURLY, or TIMESTEP)

    Raises:
        ValueError: If no matching pattern is found
    """
    file_name = file_name.lower()

    for file_type in const.FileType:
        if any(pattern in file_name for pattern in file_type.value.patterns):
            return file_type

    raise ValueError(f"No matching file type found for filename: {file_name}")


def has_pattern(file_name: str, file_type: const.FileType) -> bool:
    """
    Check if a filename contains any of the patterns associated with a specific FileType.

    Args:
        file_name (str): The name of the file to check
        file_type (FileType): The FileType enum containing patterns to match against

    Returns:
        bool: True if the filename contains any of the patterns, False otherwise
    """
    file_name = file_name.lower()
    return any(pattern in file_name for pattern in file_type.value.patterns)
