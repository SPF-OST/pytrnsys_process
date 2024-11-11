import pathlib as _pl
import typing as _tp
from collections import defaultdict as _defaultdict
from concurrent.futures import ThreadPoolExecutor

from pytrnsys_process.input.trnsys.readers import HeaderReader


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
                headers = HeaderReader.read(sim_file)
                self._index_headers(headers, sim_file.parents[1], sim_file)
            except Exception as e:
                print(f"Could not read {sim_file}: {e}")

    def init_headers_multi_thread(self):
        sim_files = self._get_files(self._get_sim_folders())

        def process_sim_file(sim_file):
            try:
                headers = HeaderReader.read(sim_file)
                self._index_headers(headers, sim_file.parents[1], sim_file)
            except Exception as e:
                print(f"Could not read {sim_file}: {e}")

        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(process_sim_file, sim_files)

    def search_header(self, header_name: str):
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


class HeadersCsv(Headers):
    RESULTS_FOLDER_NAME = "temp"
