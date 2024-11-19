import pathlib as _pl

import tests.pytrnsys_process.constants as const
from pytrnsys_process import readers


class TestReader:

    HOURLY_DIR_PATH = _pl.Path(__file__).parent / "data/hourly"
    MONTHLY_DIR_PATH = _pl.Path(__file__).parent / "data/monthly"

    def test_read_hourly(self):

        hourly_file_path = self.HOURLY_DIR_PATH / "Src_Hr.Prt"
        actual_df = readers.PrtReader().read_hourly(hourly_file_path)

        actual_file_path = self.HOURLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.HOURLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(
            encoding="UTF8"
        ) == expected_file_path.read_text(encoding="UTF8")

    def test_read_monthly(self):
        monthly_file_path = self.MONTHLY_DIR_PATH / "PCM_MO.Prt"
        actual_df = readers.PrtReader().read_monthly(monthly_file_path)

        actual_file_path = self.MONTHLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.MONTHLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(
            encoding="UTF8"
        ) == expected_file_path.read_text(encoding="UTF8")


class TestBenchmarkReader:

    def test_read_monthly_csv(self, benchmark):
        reader = readers.CsvReader()
        benchmark(reader.read, const.DATA_FOLDER / "benchmark/PCM_MO.csv")

    def test_read_monthly_prt(self, benchmark):
        reader = readers.PrtReader()
        benchmark(
            reader.read_monthly, const.DATA_FOLDER / "benchmark/PCM_MO.Prt"
        )
