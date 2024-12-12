from unittest import mock as _um

import matplotlib.testing.compare as _mpltc
import pytest

import tests.pytrnsys_process.constants as const
from pytrnsys_process import headers as h
from pytrnsys_process import readers
from pytrnsys_process.plotting import plot_wrappers as pw
from pytrnsys_process.plotting import plotters


class TestPlotters:
    SKIP_PLOT_COMPARISON = (
        False  # Toggle this to enable/disable plot comparison
    )

    @pytest.fixture
    def mock_headers(self):
        """Create a mock Headers instance with predefined columns."""
        headers = _um.Mock(spec=h.Headers)
        headers.header_index = {
            # Monthly data columns
            "QSnk60PauxCondSwitch_kW": [],
            "QSnk60dQ": [],
            "QSnk60P": [],
            "QSnk60PDhw": [],
            "QSnk60dQlossTess": [],
            "QSnk60qImbTess": [],
            # Hourly data columns
            "QSrc1TIn": [],
            "QSrc1TOut": [],
        }
        return headers

    @pytest.fixture
    def monthly_data(self):
        """Load monthly test data."""
        result_data = (
            const.DATA_FOLDER
            / "results/sim-1/temp/ENERGY_BALANCE_MO_60_TESS.Prt"
        )
        return readers.PrtReader().read_monthly(result_data)

    @pytest.fixture
    def hourly_data(self):
        """Load hourly test data."""
        result_data = const.DATA_FOLDER / "hourly/Src_Hr.Prt"
        return readers.PrtReader().read_hourly(result_data)

    def assert_plots_match(self, actual_file, expected_file, tolerance=0.001):
        """Compare two plot images for equality."""
        if self.SKIP_PLOT_COMPARISON:
            pytest.skip(
                "Plot comparison temporarily disabled during development"
            )
        assert (
            _mpltc.compare_images(
                str(actual_file), str(expected_file), tol=tolerance
            )
            is None
        )

    def test_plot_column_validation_valid(self, mock_headers, hourly_data):
        columns = ["QSrc1TIn", "QSrc1TOut"]

        with _um.patch(
                "pytrnsys_process.plotting.plotters.LinePlot._do_plot"
        ) as mock_do_plot:
            # Execute
            line_plot = plotters.LinePlot()
            line_plot.plot_with_column_validation(
                hourly_data, columns, headers=mock_headers
            )

            # Assert that _do_plot was called
            # TODO: Separate concern of column in header validation from _do_plot.  # pylint: disable=fixme
            mock_do_plot.assert_called_once()

    def test_plot_column_validation_invalid(self, mock_headers, hourly_data):
        # TODO: add this to just the validation part.   # pylint: disable=fixme
        columns = ["DoesNotExist", "AlsoMissing"]
        line_plot = plotters.LinePlot()

        with pytest.raises(ValueError) as excinfo:
            line_plot.plot_with_column_validation(
                hourly_data, columns, headers=mock_headers
            )
        assert (
                "The following columns are not available in the headers index:\nDoesNotExist\nAlsoMissing"
                in str(excinfo.value)
        )

    def test_create_stacked_bar_chart_for_monthly(self, monthly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plots/stacked-bar-chart/expected.png"
        )
        actual_file = const.DATA_FOLDER / "plots/stacked-bar-chart/actual.png"
        columns = [
            "QSnk60PauxCondSwitch_kW",
            "QSnk60dQ",
            "QSnk60P",
            "QSnk60PDhw",
            "QSnk60dQlossTess",
            "QSnk60qImbTess",
        ]

        # Execute
        fig, _ = pw.stacked_bar_chart(monthly_data, columns)
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_line_plot_for_hourly(self, hourly_data):
        # Setup
        expected_fig = const.DATA_FOLDER / "plots/line-plot/expected.png"
        actual_fig = const.DATA_FOLDER / "plots/line-plot/actual.png"
        columns = ["QSrc1TIn", "QSrc1TOut"]

        # Execute
        fig, _ = pw.line_plot(hourly_data, columns)
        fig.savefig(actual_fig)

        # Assert
        self.assert_plots_match(actual_fig, expected_fig)

    def test_create_bar_chart_for_monthly(self, monthly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plots/bar-chart/expected.png"
        actual_file = const.DATA_FOLDER / "plots/bar-chart/actual.png"
        columns = [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ]

        # Execute
        fig, _ = pw.bar_chart(monthly_data, columns)
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_histogram_for_hourly(self, hourly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plots/histogram/expected.png"
        actual_file = const.DATA_FOLDER / "plots/histogram/actual.png"
        columns = ["QSrc1TIn"]

        # Execute
        fig, _ = pw.histogram(hourly_data, columns, ylabel="Time [h]")
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_scatter_plot_for_monthly(self, monthly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plots/scatter-plot/expected.png"
        actual_file = const.DATA_FOLDER / "plots/scatter-plot/actual.png"
        columns = ["QSnk60dQlossTess", "QSnk60dQ"]

        # Execute
        fig, _ = pw.scatter_plot(
            monthly_data,
            columns,
            x_column="QSnk60dQlossTess",
            y_column="QSnk60dQ",
        )
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)
