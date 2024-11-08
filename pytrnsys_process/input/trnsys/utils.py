import pathlib as _pl
import re as _re
from collections import defaultdict as _defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as _pd

HOURLY_FILE_PATTERN = ""
TEMP = "temp"

MONTHLY_FILE_PATTERN = _re.compile(r"(_MO_|MO_|_MO|MO)$", _re.IGNORECASE)

headerIndex = _defaultdict(list)


PATH_TO_RESULTS = _pl.Path("C:/Development/data/results")


def findAllVariables(results: _pl.Path):
    allSimFolders = [item for item in results.glob("*") if item.is_dir()]
    for simFolder in allSimFolders:
        monthlyFiles = _getMonthlyFiles(simFolder / TEMP)
        for file in (simFolder / TEMP).glob("**/*"):
            try:
                df = _pd.read_csv(file, nrows=0, skiprows=1, delimiter=r"\s+")
                headers = df.columns.tolist()
                _indexHeaders(headers, simFolder, file)
            except Exception as e:
                print(f"Could not read {file}: {e}")


def _indexHeaders(headers: list[str], simFolder: _pl.Path, file: _pl.Path):
    for header in headers:
        headerIndex[header].append((simFolder.name, file.name))


def _getMonthlyFiles(path: _pl.Path) -> list[_pl.Path]:
    monthlyFiles = [
        file
        for file in path.glob("**/*")
        if file.is_file() and MONTHLY_FILE_PATTERN.search(file.name)
    ]
    return monthlyFiles


def findAllVariablesMultiThread():
    with ThreadPoolExecutor() as executor:
        files = _getAllFiles()
        futureToFile = {
            executor.submit(_processFileHeaders, file): file for file in files
        }

        for future in as_completed(futureToFile):
            results = future.result()
            for header, folder, file in results:
                headerIndex[header].append((folder, file))


def _processFileHeaders(file: _pl.Path) -> list[tuple[str, str, str]]:
    df = _pd.read_csv(file, nrows=0, skiprows=1, delimiter=r"\s+")
    headers = df.columns.tolist()
    return [(header, file.parents[1].name, file.name) for header in headers]


def _getAllFiles():
    files = []
    allSimFolders = [
        item for item in PATH_TO_RESULTS.glob("*") if item.is_dir()
    ]
    for simFolder in allSimFolders:
        for file in (simFolder / TEMP).glob("**/*"):
            files.append(file)
    return files


def searchHeader(headerName: str):
    if headerName in headerIndex:
        print(f"Header '{headerName}' found in:")
        for folder, file in headerIndex[headerName]:
            print(f"- Folder: {folder}, File: {file}")
    else:
        print(f"Header '{headerName}' not found in any files.")
