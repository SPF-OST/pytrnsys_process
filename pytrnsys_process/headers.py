import pathlib as _pl
from abc import ABC
from collections import defaultdict as _defaultdict
from concurrent.futures import ProcessPoolExecutor

from pytrnsys_process import utils
from pytrnsys_process.readers import HeaderReader


def _process_sim_file(sim_file):
    try:
        headers = HeaderReader().read_headers(sim_file)
        return headers, sim_file.parents[1], sim_file
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"Could not read {sim_file}: {e}")
        return None


class Headers:

    header_index: _defaultdict[str, list]

    def __init__(self, path_to_results: _pl.Path):
        self.path_to_results = path_to_results
        self.header_index = _defaultdict(list)

    def init_headers(self):
        sim_files = utils.get_files(
            utils.get_sim_folders(self.path_to_results)
        )
        for sim_file in sim_files:
            try:
                headers = HeaderReader().read_headers(sim_file)
                self._index_headers(headers, sim_file.parents[1], sim_file)
            except Exception as e:  # pylint: disable=broad-exception-caught

                print(f"Could not read {sim_file}: {e}")

    def init_headers_multi_process(self):
        sim_files = utils.get_files(
            utils.get_sim_folders(self.path_to_results)
        )

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

    # TODO: Add function to validate headers and log files with invalid headers  #pylint: disable=fixme


class HeaderValidationMixin(ABC):
    def validate_headers(
        self, headers: Headers, columns: list[str]
    ) -> tuple[bool, list[str]]:
        """Validates that all columns exist in the headers index.

        Parameters
        __________
            headers:
                Headers instance containing the index of available headers

            columns:
                List of column names to validate

        Returns
        _______
            Tuple of (is_valid, missing_columns): Tuple
                - is_valid: True if all columns exist
                - missing_columns: List of column names that are missing
        """
        missing_columns = []
        for column in columns:
            if column not in headers.header_index:
                missing_columns.append(column)

        return len(missing_columns) == 0, missing_columns
