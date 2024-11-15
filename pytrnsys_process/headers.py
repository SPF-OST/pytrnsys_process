import pathlib as _pl
import typing as _tp
from abc import ABC
from collections import defaultdict as _defaultdict
from concurrent.futures import ProcessPoolExecutor

from pytrnsys_process.readers import HeaderReader


def _process_sim_file(sim_file):
    try:
        headers = HeaderReader().read(sim_file)
        return headers, sim_file.parents[1], sim_file
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Could not read {sim_file}: {e}")
        return None


class Headers:

    RESULTS_FOLDER_NAME = "temp"

    header_index: _defaultdict[_tp.Any, list]

    def __init__(self, path_to_results: _pl.Path):
        self.path_to_results = path_to_results
        self.header_index = _defaultdict(list)

    def init_headers(self):
        sim_files = self._get_files(self._get_sim_folders())
        for sim_file in sim_files:
            try:
                headers = HeaderReader().read(sim_file)
                self._index_headers(headers, sim_file.parents[1], sim_file)
            except Exception as e:  # pylint: disable=broad-exception-caught

                print(f"Could not read {sim_file}: {e}")

    def init_headers_multi_process(self):
        sim_files = self._get_files(self._get_sim_folders())

        with ProcessPoolExecutor() as executor:
            results = executor.map(_process_sim_file, sim_files)
            for result in results:
                if result:
                    headers, sim_folder, sim_file = result
                    self._index_headers(headers, sim_folder, sim_file)

    # TODO: Discuss if something like this is needed # pylint: disable=fixme
    def search_header(self, header_name: str):  # pragma: no cover
        if header_name in self.header_index:
            print(f"Header '{header_name}' found in:")
            for folder, file in self.header_index[header_name]:
                print(f"- Folder: {folder}, File: {file}")
        else:
            print(f"Header '{header_name}' not found in any files.")

    def _index_headers(
        self, headers: list[str], sim_folder: _pl.Path, sim_file: _pl.Path
    ):
        for header in headers:
            self.header_index[header].append((sim_folder.name, sim_file.name))

    def _get_sim_folders(self) -> list[_pl.Path]:
        sim_folders = []
        for item in self.path_to_results.glob("*"):
            if item.is_dir():
                sim_folders.append(item)
        return sim_folders

    def _get_files(self, sim_folders: list[_pl.Path]) -> list[_pl.Path]:
        sim_files = []
        for sim_folder in sim_folders:
            for sim_file in (sim_folder / self.RESULTS_FOLDER_NAME).glob(
                "**/*"
            ):
                sim_files.append(sim_file)
        return sim_files


class HeaderValidationMixin(ABC):
    def validate_headers(
            self, headers: Headers, columns: list[str]
    ) -> tuple[bool, list[str]]:
        """Validates that all columns exist in the headers index.

        Args:
            headers: Headers instance containing the index of available headers
            columns: List of column names to validate

        Returns:
            Tuple of (is_valid, missing_columns)
            - is_valid: True if all columns exist
            - missing_columns: List of column names that are missing
        """
        missing_columns = []
        for column in columns:
            if column not in headers.header_index:
                missing_columns.append(column)

        return len(missing_columns) == 0, missing_columns


class HeadersCsv(Headers):
    RESULTS_FOLDER_NAME = "temp"
