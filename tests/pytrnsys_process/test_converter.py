import pytest as _pt

from pytrnsys_process import config as conf
from pytrnsys_process import util
from tests.pytrnsys_process import constants as test_const


class TestConverter:
    """Test suite for the CsvConverter class functionality."""

    def test_convert_sim_results_to_csv(self):
        """Test conversion of simulation results from PRT to CSV format.

        Verifies that:
        1. All expected output files are created
        2. The converted CSV file has the correct dimensions
        """
        input_dir = test_const.DATA_FOLDER / "converter/prt"
        output_dir = test_const.DATA_FOLDER / "converter/csv"

        util.CsvConverter().convert_sim_results_to_csv(input_dir, output_dir)

        expected_files = [
            "hr_control.csv",
            "hr_pcmout.csv",
            "hr_src.csv",
            "mo_energy_balance60_tess.csv",
            "mo_energy_balancehp_60.csv",
            "mo_energy_balance_hp_225.csv",
            "step_hpctrlprinter.csv",
            "step_modeprinter.csv",
            "step_pysimcooldownadd_mfr.csv",
            "step_pysimcooldownadd_t.csv",
        ]
        for file_name in expected_files:
            output_file = output_dir / file_name
            assert (
                output_file.exists()
            ), f"Expected output file {file_name} not found"

    @_pt.mark.parametrize(
        "file_type, expected_prefix",
        [
            (conf.FileType.MONTHLY, "mo_"),
            (conf.FileType.HOURLY, "hr_"),
            (conf.FileType.TIMESTEP, "step_"),
        ],
    )
    def test_rename_file_with_prefix(
        self, tmp_path, file_type, expected_prefix
    ):
        """Test file renaming functionality with different prefixes.

        Args:
            tmp_path: Pytest fixture providing temporary directory path
            file_type: FileType enum indicating the type of prefix to use
            expected_prefix: Expected prefix string to be added to filename

        Verifies that:
        1. Original file is removed after renaming
        2. New file with correct prefix exists
        """
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")

        util.CsvConverter().rename_file_with_prefix(test_file, file_type)

        assert not test_file.exists()
        assert (tmp_path / f"{expected_prefix}test.txt").exists()

    def test_rename_nonexistent_file(self, tmp_path):
        """Test that attempting to rename a nonexistent file raises FileNotFoundError."""
        nonexistent_file = tmp_path / "doesnotexist.txt"

        with _pt.raises(FileNotFoundError):
            util.CsvConverter().rename_file_with_prefix(
                nonexistent_file, conf.FileType.MONTHLY
            )
