import datetime as _dt
import pathlib as _pl

import pandas as _pd

from pytrnsys_process.input.trnsys.monthly import read_monthly_file


class Reader:

    SKIPFOOTER = 24
    HEADER = 1
    DELIMITER = r"\s+"

    @staticmethod
    def read_hourly(
        hourly_file: _pl.Path, starting_year: int = 1990
    ) -> _pd.DataFrame:
        df = _pd.read_csv(
            hourly_file,
            skipfooter=Reader.SKIPFOOTER,
            header=Reader.HEADER,
            delimiter=Reader.DELIMITER,
        )
        hours = _dt.timedelta(hours=1) * df["TIME"]
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        actual_ends_of_month = start_of_year + hours
        df = df.drop(columns=["Period", "TIME"])
        df["Timestamp"] = actual_ends_of_month
        df = df.set_index("Timestamp")
        return df

    @staticmethod
    def read_monthly(monthly_file: _pl.Path, starting_year: int = 1990):
        read_monthly_file(monthly_file, starting_year)


class HeaderReader(Reader):
    NUMBER_OF_ROWS_TO_SKIP = 1
    NUMBER_OF_ROWS = 0

    @staticmethod
    def read(sim_file: _pl.Path) -> list[str]:
        df = _pd.read_csv(
            sim_file,
            nrows=HeaderReader.NUMBER_OF_ROWS,
            skiprows=HeaderReader.NUMBER_OF_ROWS_TO_SKIP,
            delimiter=HeaderReader.DELIMITER,
        )
        return df.columns.tolist()
