import datetime as _dt
import pathlib as _pl

import pandas as _pd

from pytrnsys_process import file_matcher as fm
from pytrnsys_process import readers
from pytrnsys_process.logger import logger


class CsvConverter:

    @staticmethod
    def rename_file_with_prefix(
        file_path: _pl.Path, prefix: fm.FileType
    ) -> None:
        """Rename a file with a given prefix.

        Args:
            file_path: Path to the file to rename
            prefix: FileType enum value specifying the prefix to use

        Returns:
            Path: Path to the renamed file

        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File {file_path} does not exist")

        new_name = f"{prefix.value.prefix}{file_path.name}"
        new_path = file_path.parent / new_name
        file_path.rename(new_path)

        logger.info("Renamed %s to %s", file_path, new_path)

    def convert_sim_results_to_csv(
        self, input_path: _pl.Path, output_dir: _pl.Path
    ) -> None:
        """Convert TRNSYS simulation results to CSV format.

        Args:
            input_path: Path to input file or directory containing input files
            output_dir: Directory where CSV files will be saved

        Raises:
            ValueError: If a file doesn't match any known pattern
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        input_files = (
            [input_path] if input_path.is_file() else input_path.iterdir()
        )

        for input_file in input_files:
            if not input_file.is_file():
                continue

            if fm.has_pattern(input_file.name, fm.FileType.MONTHLY):
                df = readers.PrtReader().read_monthly(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    fm.FileType.MONTHLY.value.patterns,
                    fm.FileType.MONTHLY.value.prefix,
                )
            elif fm.has_pattern(input_file.name, fm.FileType.HOURLY):
                df = readers.PrtReader().read_hourly(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    fm.FileType.HOURLY.value.patterns,
                    fm.FileType.HOURLY.value.prefix,
                )
            elif fm.has_pattern(input_file.name, fm.FileType.TIMESTEP):
                df = readers.PrtReader().read_hourly(input_file)
                output_stem = self._refactor_filename(
                    input_file.stem,
                    fm.FileType.TIMESTEP.value.patterns,
                    fm.FileType.TIMESTEP.value.prefix,
                )
            else:
                logger.warning(
                    "Unknown file type: %s, will try to detect via timestamps",
                    input_file.name,
                )
                output_stem, df = self._detect_file_type_via_content(
                    input_file
                )

            output_file = output_dir / f"{output_stem}.csv"
            df.to_csv(output_file, index=True, encoding="UTF8")

    @staticmethod
    def _detect_file_type_via_content(
        file_path: _pl.Path,
    ) -> tuple[str, _pd.DataFrame]:
        """Detect the file type based on the content of the file."""

        df_check = readers.PrtReader().read(file_path)
        if df_check.columns[0] == "Month":
            monthly_file = f"mo_{file_path.stem}".lower()
            logger.info(
                "Converted %s to monthly file: %s", file_path, monthly_file
            )
            df_monthly = readers.PrtReader().read_monthly(file_path)
            return monthly_file, df_monthly
        df_hourly = readers.PrtReader().read_hourly(file_path)
        time_diff = df_hourly.index[1] - df_hourly.index[0]
        if time_diff < _dt.timedelta(hours=1):
            timestamp_file = f"timestamp_{file_path.stem}".lower()
            logger.info(
                "Converted %s to timestamp file: %s", file_path, timestamp_file
            )
            return timestamp_file, df_hourly
        hourly_file = f"hr_{file_path.stem}".lower()
        logger.info("Converted %s to hourly file: %s", file_path, hourly_file)
        return hourly_file, df_hourly

    @staticmethod
    def _refactor_filename(
        filename: str, patterns: list[str], prefix: str
    ) -> str:
        """Process filename by removing patterns and adding appropriate prefix."""
        processed_name = filename.lower()
        for pattern in patterns:
            processed_name = processed_name.replace(pattern, "")
        return f"{prefix}{processed_name}"
