import datetime as _dt
import pathlib as _pl
from dataclasses import dataclass

import pandas as _pd

from pytrnsys_process.logger import logger as log


# TODO: Describe what to do when file name does not match any known patterns.  # pylint: disable=fixme


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

    def read(
            self,
            file_path: _pl.Path,
            skipfooter: int = SKIPFOOTER,
            header: int = HEADER,
            delimiter: str = DELIMITER,
    ) -> _pd.DataFrame:
        """Common read function for all readers"""
        df = _pd.read_csv(
            file_path,
            skipfooter=skipfooter,
            header=header,
            delimiter=delimiter,
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
            df = self._process_dataframe(
                self.read(hourly_file), starting_year, "Period"
            )
            self._validate_hourly(df)
            return df
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
            df = self._process_dataframe(
                self.read(monthly_file), starting_year, "Month"
            )
            self._validate_monthly(df)
            return df
        except (ValueError, KeyError) as e:
            log.error("Error reading monthly file %s: %s", monthly_file, e)
            raise

    def read_step(self, step_file: _pl.Path, starting_year: int = 1990):
        df = self._process_dataframe(
            self.read(step_file, skipfooter=0, header=0), starting_year, "TIME"
        )
        return df

    def _process_dataframe(
        self, df: _pd.DataFrame, starting_year: int, time_column_name: str
    ) -> _pd.DataFrame:
        """Process the dataframe by formatting column names and creating timestamps.

        Args:
            df: DataFrame to process
            starting_year: Year to use as the start of the simulation
            time_column_name: Name of the time column ('Period' or 'Month')
        """

        # Create timestamps based on the time column type
        if time_column_name == "Period":
            df["Timestamp"] = self._create_hourly_timestamps(
                df[time_column_name].astype(float), starting_year
            )
        elif time_column_name == "Month":
            df["Timestamp"] = self._create_monthly_timestamps(
                df[time_column_name], starting_year
            )
        elif time_column_name == "TIME":
            df["Timestamp"] = self._create_step_timestamps(
                df[time_column_name].astype(float), starting_year
            )
        else:
            raise ValueError(
                f"Invalid time_column_name: {time_column_name}. Must be 'Period', 'TIME' or 'Month'"
            )

        # Remove time columns
        if df.columns[1].lower() == "time":
            df.columns.values[1] = df.columns[1].lower()
            df = df.drop(columns=["time"])
        df = df.drop(columns=[time_column_name])

        return df.set_index("Timestamp")

    def _create_step_timestamps(
            self, minutes_elapsed: _pd.Series, starting_year: int
    ) -> _pd.Series:
        """Create step timestamps from elapsed minutes since start of year.

        Args:
            minutes_elapsed: Series containing number of minutes since start of year
            starting_year: Year to use as the start of the simulation

        Returns:
            Series of datetime objects with minute intervals
        """
        minutes = [_dt.timedelta(minutes=float(m)) for m in minutes_elapsed]
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        return _pd.Series([start_of_year + m for m in minutes])

    def _create_hourly_timestamps(
        self, hours_elapsed: _pd.Series, starting_year: int
    ) -> _pd.Series:
        """Create hourly timestamps from elapsed hours since start of year.

        Args:
            hours_elapsed: Series containing number of hours since start of year
            starting_year: Year to use as the start of the simulation

        Returns:
            Series of datetime objects with hourly intervals
        """
        hours = [_dt.timedelta(hours=float(h)) for h in hours_elapsed]
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        return _pd.Series([start_of_year + h for h in hours])

    def _create_monthly_timestamps(
        self, month_names: _pd.Series, year: int = 1990
    ) -> _pd.Series:
        """Create monthly timestamps from month names.

        Args:
            month_names: Series containing month names (e.g., 'January', 'February')
            year: Year to use for the timestamps (default: 1990)

        Returns:
            Series of datetime objects set to the first day of each month
        """
        month_map = {
            month: i
            for i, month in enumerate(
                [
                    "January",
                    "February",
                    "March",
                    "April",
                    "May",
                    "June",
                    "July",
                    "August",
                    "September",
                    "October",
                    "November",
                    "December",
                ],
                1,
            )
        }

        # Convert month names to datetime objects
        timestamps = [
            _dt.datetime(year=year, month=month_map[name.strip()], day=1)
            for name in month_names
        ]
        return _pd.Series(timestamps)

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
        df = self.read(
            csv_file,
            skipfooter=self.SKIPFOOTER,
            header=self.HEADER,
            delimiter=self.DELIMITER,
        )

        df["Timestamp"] = _pd.to_datetime(df["Timestamp"])
        return df.set_index("Timestamp")
