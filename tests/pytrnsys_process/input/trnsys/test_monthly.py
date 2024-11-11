# pylint: disable=missing-module-docstring

import pathlib as _pl

import pytrnsys_process.input.trnsys.monthly as _monthly

DATA_DIR_PATH = _pl.Path(__file__).parent / "data" / "monthly" / "damian"


def test():
    monthly_file_path = DATA_DIR_PATH / "BUILDING_MO.Prt"
    actual_df = _monthly.read_monthly_file(monthly_file_path, starting_year=1990)

    actual_file_path = DATA_DIR_PATH / "actual.csv"
    actual_df.to_csv(actual_file_path, encoding="UTF8")

    expected_file_path = DATA_DIR_PATH / "expected.csv"

    assert actual_file_path.read_text(encoding="UTF8") == expected_file_path.read_text(encoding="UTF8")
