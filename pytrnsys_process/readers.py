import datetime as _dt
import pathlib as _pl
from dataclasses import dataclass

import pandas as _pd

from pytrnsys_process.logger import logger as log


# TODO: Adjust architecture to separate reading and conversion.  # pylint: disable=fixme
# TODO: Base reader with PRT and CSV as children.  # pylint: disable=fixme
# TODO: Describe what to do when file name does not match any known patterns.  # pylint: disable=fixme
# TODO: Convert single file according to keyword suggestion, and/or automatically?  # pylint: disable=fixme
# TODO: timestep from first two rows -> if 1 hour, use hourly, otherwise convert to timestep  # pylint: disable=fixme
# TODO: Message to user about automatic conversion when file name does not match any known patterns.  # pylint: disable=fixme


@dataclass
class ReaderBase:
    # ===================================
    # pylint: disable=invalid-name
    SKIPFOOTER: int = 24
    HEADER: int = 1
    DELIMITER: str = r"\s+"

    # Pylint complains about these CONSTANTS, because pylint differs with PEP8 on this topic.
    # https://stackoverflow.com/questions/25184097/pylint-invalid-constant-name/51975811#51975811
    # ===================================

    def read(self, file_path: _pl.Path) -> _pd.DataFrame:
        """Common read function for all readers"""
        df = _pd.read_csv(
            file_path,
            skipfooter=self.SKIPFOOTER,
            header=self.HEADER,
            delimiter=self.DELIMITER,
            engine="python",
        )
        return df


class PrtReader(ReaderBase):

    def read_hourly(
            self, hourly_file: _pl.Path, starting_year: int = 1990
    ) -> _pd.DataFrame:
        """Read hourly TRNSYS output data from a file.

        Args:
            hourly_file: Path to the hourly TRNSYS output file
            starting_year: Year to use as the start of the simulation (default: 1990)

        Returns:
            DataFrame with hourly data indexed by timestamp, with 'Period' and 'time' columns removed

        Raises:
            ValueError: If the timestamps are not exactly on the hour (minutes or seconds != 0)
        """
        try:
            df = self._process_dataframe(self.read(hourly_file), starting_year)
            self._validate_hourly(df)
            return df.drop(columns=["Period", "time"])
        except (ValueError, KeyError) as e:
            log.error("Error reading hourly file %s: %s", hourly_file, e)
            raise

    def read_monthly(
            self,
            monthly_file: _pl.Path,
            starting_year: int = 1990,
    ) -> _pd.DataFrame:
        """Read monthly TRNSYS output data from a file.

        Args:
            monthly_file: Path to the monthly TRNSYS output file
            starting_year: Year to use as the start of the simulation (default: 1990)

        Returns:
            DataFrame with monthly data indexed by timestamp, with 'Month' and 'time' columns removed

        Raises:
            ValueError: If the timestamps are not at the start of each month at midnight
                      (not month start or hours/minutes/seconds != 0)
        """
        try:
            df = self._process_dataframe(self.read(monthly_file), starting_year)
            self._validate_monthly(df)
            return df.drop(columns=["Month", "time"])
        except (ValueError, KeyError) as e:
            log.error("Error reading monthly file %s: %s", monthly_file, e)
            raise

    def read_step(self, step_file: _pl.Path, starting_year: int = 1990):
        df = self._process_dataframe(self.read(step_file), starting_year)
        return df.drop(columns=["Period", "time"])

    def _process_dataframe(
            self, df: _pd.DataFrame, starting_year: int
    ) -> _pd.DataFrame:
        """Process the dataframe by formatting column names and creating timestamps."""
        df.columns.values[1] = df.columns[1].lower()
        df["Timestamp"] = self._create_timestamps(
            df["time"].astype(float), starting_year
        )

        return df.set_index("Timestamp")

    def _create_timestamps(
            self, time_series: _pd.Series, starting_year: int
    ) -> _pd.Series:
        """Create timestamps from time series and starting year."""
        hours = [_dt.timedelta(hours=float(h)) for h in time_series]
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        return _pd.Series([start_of_year + h for h in hours])

    def _validate_hourly(self, df: _pd.DataFrame) -> None:
        """Validate that timestamps are exactly on the hour."""
        index = _pd.to_datetime(df.index)
        if not ((index.minute == 0) & (index.second == 0)).all():
            raise ValueError(
                "Timestamps must be exactly on the hour (minutes and seconds must be 0)"
            )

    def _validate_monthly(self, df: _pd.DataFrame) -> None:
        """Validate that timestamps are at the start of each month at midnight."""
        index = _pd.to_datetime(df.index)
        if not (
                index.is_month_start
                & (index.hour == 0)
                & (index.minute == 0)
                & (index.second == 0)
        ).all():
            raise ValueError(
                "Timestamps must be at the start of each month at midnight"
            )


@dataclass
class HeaderReader(ReaderBase):
    NUMBER_OF_ROWS_TO_SKIP = 1
    NUMBER_OF_ROWS = 0

    def read_headers(self, sim_file: _pl.Path) -> list[str]:
        df = _pd.read_csv(
            sim_file,
            nrows=self.NUMBER_OF_ROWS,
            skiprows=self.NUMBER_OF_ROWS_TO_SKIP,
            delimiter=self.DELIMITER,
        )
        return df.columns.tolist()


@dataclass
class CsvReader(ReaderBase):
    SKIPFOOTER: int = 0
    HEADER: int = 0
    DELIMITER: str = ","

    def read_csv(self, csv_file: _pl.Path) -> _pd.DataFrame:
        df = self.read(csv_file)
        return df.set_index("Timestamp")
