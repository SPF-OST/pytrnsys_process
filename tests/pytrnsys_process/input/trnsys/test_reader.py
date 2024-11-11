import pathlib as _pl

from pytrnsys_process.input.trnsys.readers import Reader


class TestReader:

    HOURLY_DIR_PATH = _pl.Path(__file__).parent / "data/hourly"
    MONTHLY_DIR_PATH = _pl.Path(__file__).parent / "data/monthly"


    def test_read_hourly(self):

        hourly_file_path = self.HOURLY_DIR_PATH / "Src_Hr.Prt"
        actual_df = Reader.read_hourly(hourly_file_path)

        actual_file_path = self.HOURLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.HOURLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(encoding="UTF8") == expected_file_path.read_text(encoding="UTF8")

    def test_read_monthly(self):

        hourly_file_path = self.MONTHLY_DIR_PATH / "PCM_MO.Prt"
        actual_df = Reader.read_monthly(hourly_file_path, starting_month=11, periods=14)

        actual_file_path = self.MONTHLY_DIR_PATH / "actual.csv"
        actual_df.to_csv(actual_file_path, encoding="UTF8")

        expected_file_path = self.MONTHLY_DIR_PATH / "expected.csv"

        assert actual_file_path.read_text(encoding="UTF8") == expected_file_path.read_text(encoding="UTF8")


