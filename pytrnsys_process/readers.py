import datetime as _dt
import pathlib as _pl

import pandas as _pd


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
        hours = _dt.timedelta(hours=1) * df["TIME"]  # type: ignore
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        actual_ends_of_month = start_of_year + hours
        df = df.drop(columns=["Period", "TIME"])
        df["Timestamp"] = actual_ends_of_month
        df = df.set_index("Timestamp")
        return df

    @staticmethod
    def read_monthly(
        monthly_file: _pl.Path,
        starting_year: int = 1990,
        starting_month: int = 1,
        periods: int = 12,
    ) -> _pd.DataFrame:
        df = _pd.read_csv(
            monthly_file,
            skipfooter=Reader.SKIPFOOTER,
            header=Reader.HEADER,
            delimiter=Reader.DELIMITER,
        )
        hours = _dt.timedelta(hours=1) * df["TIME"]  # type: ignore
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        actual_ends_of_month = start_of_year + hours
        expected_ends_of_months = _pd.date_range(
            _dt.datetime(day=1, month=starting_month, year=starting_year),
            periods=periods,
            freq="ME",
        ) + _dt.timedelta(days=1)
        if (actual_ends_of_month != expected_ends_of_months).any():
            raise ValueError(
                f"The time stamps of the supposedly monthly file '{monthly_file}' don't fall on the end of each month."
            )
        df = df.drop(columns=["Month", "TIME"])
        formatted_ends_of_month = [
            timestamp.strftime("%m-%y") for timestamp in actual_ends_of_month
        ]
        df["Timestamp"] = formatted_ends_of_month
        df = df.set_index("Timestamp")

        return df


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
