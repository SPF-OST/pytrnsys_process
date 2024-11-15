import datetime as _dt
import pathlib as _pl
from dataclasses import dataclass

import pandas as _pd


@dataclass
class Reader:
    # pylint: disable=invalid-name
    SKIPFOOTER: int = 24
    HEADER: int = 1
    DELIMITER: str = r"\s+"

    def _read_common(
            self, file_path: _pl.Path, starting_year: int = 1990
    ) -> _pd.DataFrame:
        """Common reading logic for both hourly and monthly data."""
        df = _pd.read_csv(
            file_path,
            skipfooter=self.SKIPFOOTER,
            header=self.HEADER,
            delimiter=self.DELIMITER,
        )
        df.columns.values[1] = df.columns[1].lower()
        # Extract timestamp creation to a separate method
        df["Timestamp"] = self._create_timestamps(
            df["time"].astype(float), starting_year
        )
        return df.set_index("Timestamp")

    def _create_timestamps(
            self, time_series: _pd.Series, starting_year: int
    ) -> _pd.Series:
        """Create timestamps from time series and starting year."""
        # Convert to list of timedelta
        hours = [_dt.timedelta(hours=float(h)) for h in time_series]
        start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
        return _pd.Series([start_of_year + h for h in hours])

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
        df = self._read_common(hourly_file, starting_year)
        self._validate_hourly(df)
        return df.drop(columns=["Period", "time"])

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
        df = self._read_common(monthly_file, starting_year)
        df = df.drop(columns=["Month", "time"])
        self._validate_monthly(df)
        return df

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
class HeaderReader(Reader):
    NUMBER_OF_ROWS_TO_SKIP = 1
    NUMBER_OF_ROWS = 0

    def read(self, sim_file: _pl.Path) -> list[str]:
        df = _pd.read_csv(
            sim_file,
            nrows=self.NUMBER_OF_ROWS,
            skiprows=self.NUMBER_OF_ROWS_TO_SKIP,
            delimiter=self.DELIMITER,
        )
        return df.columns.tolist()
