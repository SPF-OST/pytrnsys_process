import pathlib as _pl
import subprocess
from unittest.mock import Mock, call, patch

import matplotlib.pyplot as plt

from pytrnsys_process import process_batch as pb
from pytrnsys_process import utils
from pytrnsys_process.settings import settings
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")


def test_save_plot_for_default_settings(tmp_path):
    fig = Mock(spec=plt.Figure)

    with (
        patch("pytrnsys_process.utils.convert_svg_to_emf") as mock_convert,
        patch("os.remove") as mock_remove,
    ):
        # Call save_plot
        utils.export_plots_in_configured_formats(fig, tmp_path, "test_plot")

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
        utils.convert_svg_to_emf(file_no_suffix)

        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with(
            [
                settings.plot.inkscape_path,
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
        patch("pytrnsys_process.utils.log.main_logger") as mock_logger,
    ):
        svg_path = tmp_path / "test.svg"
        utils.convert_svg_to_emf(svg_path)

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
        patch("pytrnsys_process.utils.log.main_logger") as mock_logger,
    ):
        svg_path = tmp_path / "test.svg"
        utils.convert_svg_to_emf(svg_path)

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
    files = utils.get_files([sim_folder])

    # Verify results
    assert len(files) == 1
    assert all(f.is_file() for f in files)
    assert nested_folder not in files
    assert results_folder not in files
    assert set(files) == {test_file1}


def test_get_file_content_as_string(tmp_path):
    test_file = tmp_path / "test.txt"
    expected_content = "Hello\nWorld!"
    test_file.write_text(expected_content, encoding="UTF-8")

    result = utils.get_file_content_as_string(test_file)
    assert result == expected_content


def test_simulation_pickle(tmp_path):
    sim_pickle = tmp_path / "simulation.pickle"
    sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
    simulation = pb.process_single_simulation(
        sim_folder, lambda x: None
    )

    utils.save_to_pickle(simulation, sim_pickle)
    sim_from_pickle = utils.load_simulation_from_pickle(sim_pickle)

    assert sim_from_pickle.monthly.shape == (14, 11)
    assert sim_from_pickle.hourly.shape == (3, 18)
    assert sim_from_pickle.scalar.shape == (1, 10)
    assert sim_from_pickle.step.shape == (0, 0)


def test_simulations_data_pickle(tmp_path):
    simulation_data_pickle = tmp_path / "simulations_data.pickle"
    sim_folder = _pl.Path(RESULTS_FOLDER)
    simulations_data = pb.process_whole_result_set(
        sim_folder, lambda x: None
    )

    utils.save_to_pickle(simulations_data, simulation_data_pickle)
    simulations_data_from_pickle = utils.load_simulations_data_from_pickle(simulation_data_pickle)

    assert simulations_data_from_pickle.simulations["sim-1"].hourly.shape == (3, 18)
    assert simulations_data_from_pickle.simulations["sim-1"].monthly.shape == (14, 11)
    assert simulations_data_from_pickle.simulations["sim-1"].step.shape == (0, 0)
    assert simulations_data_from_pickle.simulations["sim-2"].hourly.shape == (0, 0)
    assert simulations_data_from_pickle.simulations["sim-2"].monthly.shape == (14, 11)
    assert simulations_data_from_pickle.simulations["sim-2"].step.shape == (0, 0)
    assert simulations_data_from_pickle.scalar.shape == (2, 10)
