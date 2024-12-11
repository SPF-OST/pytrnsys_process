import datetime as _dt
import pathlib as _pl
import re as _re

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

    Raises:
        ValueError: If the file type cannot be determined from the content
    """
    reader = readers.PrtReader()

    try:
        # First try reading as regular file to check if it's monthly or hourly
        monthly_or_hourly_df = reader.read(file_path)
        if monthly_or_hourly_df.columns[0] == "Month":
            logger.info("Detected %s as monthly file", file_path)
            return const.FileType.MONTHLY
        if monthly_or_hourly_df.columns[0] == "Period":
            logger.info("Detected %s as hourly file", file_path)
            return const.FileType.HOURLY
        # Try reading as step file
        step_df = reader.read_step(file_path)
        if not step_df.empty:
            time_interval = step_df.index[1] - step_df.index[0]
            if time_interval < _dt.timedelta(hours=1):
                logger.info("Detected %s as step file", file_path)
                return const.FileType.TIMESTEP
    except Exception as e:
        logger.error("Error reading file %s: %s", file_path, str(e))
        raise ValueError(f"Failed to read file {file_path}: {str(e)}") from e

    # If we get here, file type could not be determined
    raise ValueError(
        f"Could not determine file type from content of {file_path}"
    )


def get_file_type_using_file_name(file: _pl.Path) -> const.FileType:
    """
    Determine the file type by checking the filename against known patterns.

    Args:
        file (Path): The path to the file to check

    Returns:
        FileType: The detected file type (MONTHLY, HOURLY, or TIMESTEP)

    Raises:
        ValueError: If no matching pattern is found
    """
    file_name = file.stem.lower()

    for file_type in const.FileType:
        if any(
                _re.search(pattern, file_name)
                for pattern in file_type.value.patterns
        ):
            return file_type

    logger.warning("No matching file type found for filename: %s", file_name)
    raise ValueError(f"No matching file type found for filename: {file_name}")


def has_pattern(file: _pl.Path, file_type: const.FileType) -> bool:
    """
    Check if a filename contains any of the patterns associated with a specific FileType.

    Args:
        file (Path): The path to the file to check
        file_type (FileType): The FileType enum containing patterns to match against

    Returns:
        bool: True if the filename contains any of the patterns, False otherwise
    """
    file_name = file.stem.lower()
    return any(
        _re.search(pattern, file_name) for pattern in file_type.value.patterns
    )
