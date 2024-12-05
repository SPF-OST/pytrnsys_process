import subprocess
from unittest.mock import Mock, call, patch

import matplotlib.pyplot as plt

from pytrnsys_process import utils
from pytrnsys_process.settings import settings


def test_save_plot_for_default_settings(tmp_path):
    fig = Mock(spec=plt.Figure)

    with patch("pytrnsys_process.utils.convert_svg_to_emf") as mock_convert:
        # Call save_plot
        utils.save_plot(fig, tmp_path, "test_plot")

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
            call(plots_dir / "test_plot-A4.svg"),
            call(plots_dir / "test_plot-A4_HALF.svg"),
        ]
        assert mock_convert.call_args_list == expected_convert_calls


def test_convert_svg_to_emf(tmp_path):
    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("subprocess.run") as mock_run,
        patch("os.remove") as mock_remove,
    ):
        # Create test SVG path
        svg_path = tmp_path / "test.svg"

        # Call convert_svg_to_emf
        utils.convert_svg_to_emf(svg_path)

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
        mock_remove.assert_called_once_with(svg_path)


def test_convert_svg_to_emf_inkscape_not_found(tmp_path):
    with (
        patch("pathlib.Path.exists", return_value=False),
        patch("pytrnsys_process.utils.logger") as mock_logger,
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
        patch("pytrnsys_process.utils.logger") as mock_logger,
    ):
        svg_path = tmp_path / "test.svg"
        utils.convert_svg_to_emf(svg_path)

        # Verify error was logged
        mock_logger.error.assert_called_once()
        assert (
                "Inkscape conversion failed" in mock_logger.error.call_args[0][0]
        )
