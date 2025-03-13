import pathlib as _pl
import pickle
import subprocess
from unittest.mock import Mock, call, patch

import matplotlib.pyplot as plt
import pytest as _pt

from pytrnsys_process import config as conf
from pytrnsys_process import process
from pytrnsys_process import util
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")


# Test classes for pickle tests
class IncompleteSim:
    """Test class for simulation with missing attributes."""

    def __init__(self):
        self.monthly = None
        self.hourly = None
        # Missing: step, scalar, path


class IncompleteSimData:
    """Test class for simulations data with missing attributes."""

    def __init__(self):
        self.simulations = {}
        # Missing: scalar, path_to_simulations


def test_save_plot_for_default_settings(tmp_path):
    fig = Mock(spec=plt.Figure)

    with (
        patch(
            "pytrnsys_process.util.utils.convert_svg_to_emf"
        ) as mock_convert,
        patch("os.remove") as mock_remove,
    ):
        # Call save_plot
        util.export_plots_in_configured_formats(fig, tmp_path, "test_plot")

        # Verify plots directory was created
        plots_dir = tmp_path / "plots"
        assert plots_dir.exists()

        # Verify figure size was set for each size
        expected_set_size_calls = [call((7.8, 3.9)), call((3.8, 3.9))]
        assert fig.set_size_inches.call_args_list == expected_set_size_calls

        # Verify savefig was called for each format and size
        expected_savefig_calls = [
            call(plots_dir / "test_plot-A4.png"),
            call(plots_dir / "test_plot-A4.pdf"),
            call(plots_dir / "test_plot-A4.svg"),
            call(plots_dir / "test_plot-A4_HALF.png"),
            call(plots_dir / "test_plot-A4_HALF.pdf"),
            call(plots_dir / "test_plot-A4_HALF.svg"),
        ]
        assert fig.savefig.call_args_list == expected_savefig_calls

        # Verify convert_svg_to_emf was called for each size
        expected_convert_calls = [
            call(plots_dir / "test_plot-A4"),
            call(plots_dir / "test_plot-A4_HALF"),
        ]
        assert mock_convert.call_args_list == expected_convert_calls
        assert mock_remove.call_count == 2


def test_convert_svg_to_emf(tmp_path):
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("subprocess.run") as mock_run,
        patch("os.remove") as mock_remove,
    ):
        # Create test SVG path
        svg_path = tmp_path / "test.svg"
        file_no_suffix = tmp_path / "test"

        # Call convert_svg_to_emf
        util.convert_svg_to_emf(file_no_suffix)

        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with(
            [
                conf.global_settings.plot.inkscape_path,
                "--export-filename=" + str(tmp_path / "test.emf"),
                "--export-type=emf",
                str(svg_path),
            ],
            check=True,
            capture_output=True,
            text=True,
        )

        # Verify original SVG was removed
        assert not mock_remove.called


def test_convert_svg_to_emf_inkscape_not_found(tmp_path):
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("pytrnsys_process.log.default_console_logger") as mock_logger,
    ):
        svg_path = tmp_path / "test.svg"
        util.convert_svg_to_emf(svg_path)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert (
            "System error running Inkscape: %s"
            in mock_logger.error.call_args[0][0]
        )


def test_convert_svg_to_emf_subprocess_error(tmp_path):
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch(
            "subprocess.run",
            side_effect=subprocess.CalledProcessError(1, [], output="error"),
        ),
        patch("pytrnsys_process.log.default_console_logger") as mock_logger,
    ):
        svg_path = tmp_path / "test.svg"
        util.convert_svg_to_emf(svg_path)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert (
            "Inkscape conversion failed" in mock_logger.error.call_args[0][0]
        )


def test_get_files_works_as_expected(tmp_path):
    # Create test directory structure
    sim_folder = tmp_path / "sim1"
    results_folder = sim_folder / "temp"
    nested_folder = results_folder / "nested"

    # Create directories
    for folder in [sim_folder, results_folder, nested_folder]:
        folder.mkdir(parents=True)

    # Create some test files
    test_file1 = results_folder / "test1.prt"
    test_file2 = nested_folder / "test2.prt"
    test_file1.touch()
    test_file2.touch()

    # Run the function
    files = util.get_files([sim_folder])

    # Verify results
    assert len(files) == 1
    assert all(f.is_file() for f in files)
    assert nested_folder not in files
    assert results_folder not in files
    assert set(files) == {test_file1}


def test_get_file_content_as_string_windows_1252(tmp_path):
    test_file = tmp_path / "test.txt"
    expected_content = "Hello\nWorld! °"
    test_file.write_text(expected_content, encoding="windows-1252")

    result = util.get_file_content_as_string(test_file)
    assert result == expected_content

def test_get_file_content_as_string_utf_8(tmp_path):
    test_file = tmp_path / "test.txt"
    expected_content = "Hello\nWorld! °"
    test_file.write_text(expected_content, encoding="UTF-8")

    result = util.get_file_content_as_string(test_file)
    assert result == expected_content

def test_get_file_content_as_string_force_utf_8(tmp_path):
    test_file = tmp_path / "test.txt"
    expected_content = "Hello\nWorld! °"
    test_file.write_text(expected_content, encoding="windows-1252")

    with _pt.raises(UnicodeDecodeError):
        util.get_file_content_as_string(test_file, encoding="UTF-8")

def test_simulation_pickle(tmp_path):
    sim_pickle = tmp_path / "simulation.pickle"
    sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
    simulation = process.process_single_simulation(sim_folder, lambda x: None)

    util.save_to_pickle(simulation, sim_pickle)
    sim_from_pickle = util.load_simulation_from_pickle(sim_pickle)

    assert sim_from_pickle.monthly.shape == (14, 11)
    assert sim_from_pickle.hourly.shape == (3, 18)
    assert sim_from_pickle.scalar.shape == (1, 10)
    assert sim_from_pickle.step.shape == (0, 0)


def test_simulations_data_pickle(tmp_path):
    simulation_data_pickle = tmp_path / "simulations_data.pickle"
    sim_folder = _pl.Path(RESULTS_FOLDER)
    simulations_data = process.process_whole_result_set(
        sim_folder, lambda x: None
    )

    util.save_to_pickle(simulations_data, simulation_data_pickle)
    simulations_data_from_pickle = util.load_simulations_data_from_pickle(
        simulation_data_pickle
    )

    assert simulations_data_from_pickle.simulations["sim-1"].hourly.shape == (
        3,
        18,
    )
    assert simulations_data_from_pickle.simulations["sim-1"].monthly.shape == (
        14,
        11,
    )
    assert simulations_data_from_pickle.simulations["sim-1"].step.shape == (
        0,
        0,
    )
    assert simulations_data_from_pickle.simulations["sim-2"].hourly.shape == (
        0,
        0,
    )
    assert simulations_data_from_pickle.simulations["sim-2"].monthly.shape == (
        14,
        11,
    )
    assert simulations_data_from_pickle.simulations["sim-2"].step.shape == (
        0,
        0,
    )
    assert simulations_data_from_pickle.scalar.shape == (2, 10)


def test_load_simulation_from_invalid_pickle(tmp_path):
    """Test loading a simulation from an invalid pickle file."""
    invalid_pickle = tmp_path / "invalid.pickle"
    with open(invalid_pickle, "wb") as f:
        f.write(b"not a pickle file")

    with _pt.raises(pickle.UnpicklingError):
        util.load_simulation_from_pickle(invalid_pickle)


def test_load_simulation_from_missing_file(tmp_path):
    """Test loading a simulation from a non-existent file."""
    missing_file = tmp_path / "does_not_exist.pickle"

    with _pt.raises(OSError):
        util.load_simulation_from_pickle(missing_file)


def test_load_simulation_with_missing_attributes(tmp_path):
    """Test loading a simulation object that's missing required attributes."""
    incomplete_sim_pickle = tmp_path / "incomplete_sim.pickle"

    with open(incomplete_sim_pickle, "wb") as f:
        pickle.dump(IncompleteSim(), f)

    with _pt.raises(ValueError) as exc_info:
        util.load_simulation_from_pickle(incomplete_sim_pickle)
    assert "missing required Simulation attributes" in str(exc_info.value)


def test_load_simulations_data_from_invalid_pickle(tmp_path):
    """Test loading simulations data from an invalid pickle file."""
    invalid_pickle = tmp_path / "invalid.pickle"
    with open(invalid_pickle, "wb") as f:
        f.write(b"not a pickle file")

    with _pt.raises(pickle.UnpicklingError):
        util.load_simulations_data_from_pickle(invalid_pickle)


def test_load_simulations_data_from_missing_file(tmp_path):
    """Test loading simulations data from a non-existent file."""
    missing_file = tmp_path / "does_not_exist.pickle"

    with _pt.raises(OSError):
        util.load_simulations_data_from_pickle(missing_file)


def test_load_simulations_data_with_missing_attributes(tmp_path):
    """Test loading a simulations data object that's missing required attributes."""
    incomplete_data_pickle = tmp_path / "incomplete_data.pickle"

    with open(incomplete_data_pickle, "wb") as f:
        pickle.dump(IncompleteSimData(), f)

    with _pt.raises(ValueError) as exc_info:
        util.load_simulations_data_from_pickle(incomplete_data_pickle)
    assert "missing required SimulationsData attributes" in str(exc_info.value)
