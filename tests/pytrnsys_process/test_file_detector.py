import pathlib as _pl

import pytest

from pytrnsys_process import config as conf
from pytrnsys_process import process
from tests.pytrnsys_process import constants as test_const

# Test data for file name based tests
FILE_NAME_TEST_CASES = [
    (_pl.Path("results_mo_test.txt"), conf.FileType.MONTHLY),
    (_pl.Path("results_mo.txt"), conf.FileType.MONTHLY),
    (_pl.Path("mo_results.txt"), conf.FileType.MONTHLY),
    (_pl.Path("results_hr_test.txt"), conf.FileType.HOURLY),
    (_pl.Path("results_hr.txt"), conf.FileType.HOURLY),
    (_pl.Path("hr_results.txt"), conf.FileType.HOURLY),
    (_pl.Path("results_step_test.txt"), conf.FileType.TIMESTEP),
    (_pl.Path("step_results.txt"), conf.FileType.TIMESTEP),
    (_pl.Path("step_modeprinter.csv"), conf.FileType.TIMESTEP),
    (_pl.Path("this_is_a_deck_file.dck"), conf.FileType.DECK),
    (_pl.Path("pytrnsys_demo_Mfr.prt"), conf.FileType.TIMESTEP),
]


def test_get_file_type_using_file_name():
    """Test file type detection based on file names"""
    for file_path, expected_type in FILE_NAME_TEST_CASES:
        assert (
                process.get_file_type_using_file_name(file_path) == expected_type
        )


def test_get_file_type_using_file_name_invalid():
    """Test that invalid file names raise ValueError"""
    with pytest.raises(ValueError):
        process.get_file_type_using_file_name(_pl.Path("test.mo"))


def test_has_pattern():
    """Test pattern matching functionality"""
    assert (
            process.has_pattern(
                _pl.Path("results_mo_test.txt"), conf.FileType.MONTHLY
            )
            is True
    )
    assert (
            process.has_pattern(
                _pl.Path("results_hr_test.txt"), conf.FileType.MONTHLY
            )
            is False
    )
    assert (
            process.has_pattern(
                _pl.Path("results_hr_test.txt"), conf.FileType.HOURLY
            )
            is True
    )
    assert (
            process.has_pattern(
                _pl.Path("results_step_test.txt"), conf.FileType.TIMESTEP
            )
            is True
    )


class TestFileContentDetection:
    @pytest.fixture
    def monthly_file(self):
        file_path = (
            test_const.DATA_FOLDER
            / "results/sim-1/temp/ENERGY_BALANCE_MO_60_TESS.Prt"
        )
        return file_path

    @pytest.fixture
    def hourly_file(self):
        file_path = test_const.DATA_FOLDER / "results/sim-1/temp/control.prt"
        return file_path

    @pytest.fixture
    def timestep_file(self):
        file_path = (
            test_const.DATA_FOLDER / "results/sim-1/temp/HPCtrlPrinter.Prt"
        )
        return file_path

    def test_detect_monthly_file(self, monthly_file):
        """Test detection of monthly files based on content"""
        assert (
                process.get_file_type_using_file_content(monthly_file)
                == conf.FileType.MONTHLY
        )

    def test_detect_hourly_file(self, hourly_file):
        """Test detection of hourly files based on content"""
        assert (
                process.get_file_type_using_file_content(hourly_file)
                == conf.FileType.HOURLY
        )

    def test_detect_timestep_file(self, timestep_file):
        """Test detection of timestep files based on content"""
        assert (
                process.get_file_type_using_file_content(timestep_file)
                == conf.FileType.TIMESTEP
        )
