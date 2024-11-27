import pytest as _pt

import tests.pytrnsys_process.constants as const
from pytrnsys_process import converter, readers, file_matcher as fm


class TestConverter:
    """Test suite for the CsvConverter class functionality."""

    def test_convert_sim_results_to_csv(self):
        """Test conversion of simulation results from PRT to CSV format.

        Verifies that:
        1. All expected output files are created
        2. The converted CSV file has the correct dimensions
        """
        input_dir = const.DATA_FOLDER / "conversion/prt"
        output_dir = const.DATA_FOLDER / "conversion/csv"

        converter.CsvConverter().convert_sim_results_to_csv(
            input_dir, output_dir
        )

        expected_files = [
            "hr_control.csv",
            "hr_pcmout.csv",
            "hr_src.csv",
            "mo_energy_balance131_tess.csv",
            "mo_energy_balance183_tess.csv",
            "mo_pcm.csv",
        ]
        for file_name in expected_files:
            output_file = output_dir / file_name
            assert (
                output_file.exists()
            ), f"Expected output file {file_name} not found"

        shape = readers.CsvReader().read(
            const.DATA_FOLDER / "conversion/csv/mo_energy_balance131_tess.csv"
        ).shape == (14, 7)
        assert shape

    @_pt.mark.parametrize(
        "file_type, expected_prefix",
        [
            (fm.FileType.MONTHLY, "mo_"),
            (fm.FileType.HOURLY, "hr_"),
            (fm.FileType.TIMESTEP, "step_"),
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

        converter.CsvConverter().rename_file_with_prefix(test_file, file_type)

        assert not test_file.exists()
        assert (tmp_path / f"{expected_prefix}test.txt").exists()

    def test_rename_nonexistent_file(self, tmp_path):
        """Test that attempting to rename a nonexistent file raises FileNotFoundError."""
        nonexistent_file = tmp_path / "doesnotexist.txt"

        with _pt.raises(FileNotFoundError):
            converter.CsvConverter().rename_file_with_prefix(
                nonexistent_file, fm.FileType.MONTHLY
            )
