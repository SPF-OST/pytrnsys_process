import pytest

from pytrnsys_process import constants as const
from pytrnsys_process import file_matcher as fm
from tests.pytrnsys_process import constants as test_const

# Test data for file name based tests
FILE_NAME_TEST_CASES = [
    ("results_mo_test.txt", const.FileType.MONTHLY),
    ("results_mo.txt", const.FileType.MONTHLY),
    ("results.mo", const.FileType.MONTHLY),
    ("mo_results.txt", const.FileType.MONTHLY),
    ("results_hr_test.txt", const.FileType.HOURLY),
    ("results_hr.txt", const.FileType.HOURLY),
    ("results.hr", const.FileType.HOURLY),
    ("hr_results.txt", const.FileType.HOURLY),
    ("results_step_test.txt", const.FileType.TIMESTEP),
    ("step_results.txt", const.FileType.TIMESTEP),
]


def test_get_file_type_using_file_name():
    """Test file type detection based on file names"""
    for file_name, expected_type in FILE_NAME_TEST_CASES:
        assert fm.get_file_type_using_file_name(file_name) == expected_type


def test_get_file_type_using_file_name_invalid():
    """Test that invalid file names raise ValueError"""
    with pytest.raises(ValueError):
        fm.get_file_type_using_file_name("invalid_file_name.txt")


def test_has_pattern():
    """Test pattern matching functionality"""
    assert (
            fm.has_pattern("results_mo_test.txt", const.FileType.MONTHLY) is True
    )
    assert (
            fm.has_pattern("results_hr_test.txt", const.FileType.MONTHLY) is False
    )
    assert fm.has_pattern("results_hr_test.txt", const.FileType.HOURLY) is True
    assert (
            fm.has_pattern("results_step_test.txt", const.FileType.TIMESTEP)
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
        file_path = (
                test_const.DATA_FOLDER / "results/sim-1/temp/control_hr.prt"
        )
        return file_path

    @pytest.fixture
    def timestep_file(self):
        file_path = (
                test_const.DATA_FOLDER
            / "results/sim-1/temp/sink_storage_temperatures_step.prt"
        )
        return file_path

    def test_detect_monthly_file(self, monthly_file):
        """Test detection of monthly files based on content"""
        assert (
            fm.get_file_type_using_file_content(monthly_file)
            == const.FileType.MONTHLY
        )

    def test_detect_hourly_file(self, hourly_file):
        """Test detection of hourly files based on content"""
        assert (
            fm.get_file_type_using_file_content(hourly_file)
            == const.FileType.HOURLY
        )

    @pytest.mark.skip(reason="Skipped until step file requirements are clear")
    def test_detect_timestep_file(self, timestep_file):
        """Test detection of timestep files based on content"""
        assert (
            fm.get_file_type_using_file_content(timestep_file)
            == const.FileType.TIMESTEP
        )
