import pandas as _pd

import tests.pytrnsys_process.constants as test_const
from pytrnsys_process import read


class TestReader:

    HOURLY_DIR_PATH = test_const.DATA_FOLDER / "reader/hourly"
    MONTHLY_DIR_PATH = test_const.DATA_FOLDER / "reader/monthly"
    STEP_DIR_PATH = test_const.DATA_FOLDER / "reader/step"

    def test_read_hourly(self):

        hourly_file_path = self.HOURLY_DIR_PATH / "Src_Hr.Prt"
        actual_df = read.PrtReader().read_hourly(hourly_file_path)

        actual_file_path = self.HOURLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.HOURLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(
            encoding="UTF8"
        ) == expected_file_path.read_text(encoding="UTF8")

    def test_read_monthly(self):
        monthly_file_path = self.MONTHLY_DIR_PATH / "PCM_MO.Prt"
        actual_df = read.PrtReader().read_monthly(monthly_file_path)

        actual_file_path = self.MONTHLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.MONTHLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(
            encoding="UTF8"
        ) == expected_file_path.read_text(encoding="UTF8")

        # Verify timestamps are correct
        timestamps = actual_df.index
        assert len(timestamps) == 14
        assert timestamps[0].year == 1990
        assert timestamps[0].month == 11
        assert timestamps[-1].year == 1991
        assert timestamps[-1].month == 12

    def test_read_step_hydraulic(self):
        step_file_path = self.STEP_DIR_PATH / "Icegrid_ARA_existing_2022_T.prt"
        actual_df = read.PrtReader().read_step(step_file_path)

        expected_file_path = self.STEP_DIR_PATH / "expected.csv"
        expected_df = read.CsvReader().read_csv(expected_file_path)

        _pd.testing.assert_frame_equal(actual_df, expected_df)

    def test_read_step_other(self):
        step_file_path = (
            self.STEP_DIR_PATH / "sink_storage_temperatures_step.prt"
        )
        actual_df = read.PrtReader().read_step(
            step_file_path, skipfooter=23, header=1
        )

        expected_file_path = self.STEP_DIR_PATH / "expected_other.csv"
        expected_df = read.CsvReader().read_csv(expected_file_path)
        _pd.testing.assert_frame_equal(actual_df, expected_df)


class TestBenchmarkReader:

    def test_read_monthly_csv(self, benchmark):
        reader = read.CsvReader()
        benchmark(
            reader.read, test_const.DATA_FOLDER / "reader/benchmark/PCM_MO.csv"
        )

    def test_read_monthly_prt(self, benchmark):
        reader = read.PrtReader()
        benchmark(
            reader.read_monthly,
            test_const.DATA_FOLDER / "reader/benchmark/PCM_MO.Prt",
        )
