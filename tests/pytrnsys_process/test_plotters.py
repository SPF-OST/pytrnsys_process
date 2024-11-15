import unittest.mock as _um

import matplotlib.testing.compare as _mpltc
import pytest

import tests.pytrnsys_process.constants as const
from pytrnsys_process import plotters as plt
from pytrnsys_process.headers import Headers
from pytrnsys_process.readers import Reader


class TestPlotters:
    SKIP_PLOT_COMPARISON = (
        True  # Toggle this to enable/disable plot comparison
    )

    @pytest.fixture
    def mock_headers(self):
        """Create a mock Headers instance with predefined columns."""
        headers = _um.Mock(spec=Headers)
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
        return Reader().read_monthly(result_data)

    @pytest.fixture
    def hourly_data(self):
        """Load hourly test data."""
        result_data = const.DATA_FOLDER / "hourly/Src_Hr.Prt"
        return Reader().read_hourly(result_data)

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

    def test_create_stacked_bar_chart_for_monthly(
            self, mock_headers, monthly_data
    ):
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
        monthly_bar_chart = plt.StackedBarChart()
        fig = monthly_bar_chart.plot(
            monthly_data, columns, headers=mock_headers
        )
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_line_plot_for_hourly(self, mock_headers, hourly_data):
        # Setup
        expected_fig = const.DATA_FOLDER / "plots/line-plot/expected.png"
        actual_fig = const.DATA_FOLDER / "plots/line-plot/actual.png"
        columns = ["QSrc1TIn", "QSrc1TOut"]

        # Execute
        line_plot = plt.LinePlot()
        fig = line_plot.plot(hourly_data, columns, headers=mock_headers)
        fig.savefig(actual_fig)

        # Assert
        self.assert_plots_match(actual_fig, expected_fig)

    def test_create_bar_chart_for_monthly(self, mock_headers, monthly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plots/bar-chart/expected.png"
        actual_file = const.DATA_FOLDER / "plots/bar-chart/actual.png"
        columns = [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ]

        # Execute
        bar_chart = plt.BarChart()
        fig = bar_chart.plot(monthly_data, columns, headers=mock_headers)
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)
