import pathlib as _pl
from dataclasses import dataclass

import pandas as _pd

from pytrnsys_process import constants as const
from pytrnsys_process import file_type_detector as fm
from pytrnsys_process import readers, utils
from pytrnsys_process.logger import main_logger


@dataclass
class SimFile:
    name: str
    type: const.FileType
    data: _pd.DataFrame


@dataclass
class Simulation:
    name: str
    files: list[SimFile]


def process_simulation(
    sim_folder: _pl.Path, detect_file_using_content: bool = False
) -> Simulation:
    sim_files = utils.get_files([sim_folder])
    files = []
    for sim_file in sim_files:
        try:
            if detect_file_using_content:
                files.append(process_file_using_file_content(sim_file))
            else:
                files.append(process_file_using_file_name(sim_file))
        except ValueError as e:
            main_logger.warning(
                "Error reading file %s it will not be available for processing: %s",
                sim_file,
                str(e),
                exc_info=True,
            )
    return Simulation(sim_folder.name, files)


def process_file_using_file_content(file_path: _pl.Path) -> SimFile:
    file_type = fm.get_file_type_using_file_content(file_path)
    reader = readers.PrtReader()
    if file_type == const.FileType.MONTHLY:
        data = reader.read_monthly(file_path)
    elif file_type == const.FileType.HOURLY:
        data = reader.read_hourly(file_path)
    elif file_type == const.FileType.TIMESTEP:
        data = reader.read_step(file_path)
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    return SimFile(file_path.name, file_type, data)


def process_file_using_file_name(file_path: _pl.Path) -> SimFile:
    file_type = fm.get_file_type_using_file_name(file_path)
    reader = readers.PrtReader()
    if file_type == const.FileType.MONTHLY:
        data = reader.read_monthly(file_path)
    elif file_type == const.FileType.HOURLY:
        data = reader.read_hourly(file_path)
    elif file_type == const.FileType.TIMESTEP:
        data = reader.read_step(file_path)
    else:
        raise ValueError(f"Unknown file type: {file_type}")

    return SimFile(file_path.name, file_type, data)
