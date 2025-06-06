import matplotlib.testing.compare as _mpltc
import pandas as _pd
import pytest as _pt

import tests.pytrnsys_process.constants as const
from pytrnsys_process import read
from pytrnsys_process.plot import plot_wrappers as plot


# pylint: disable=too-many-public-methods
class TestPlotters:
    SKIP_PLOT_COMPARISON = (
        False  # Toggle this to enable/disable plot comparison
    )

    @_pt.fixture
    def monthly_data(self):
        """Load monthly test data."""
        result_data = (
            const.DATA_FOLDER / "plotters/data/ENERGY_BALANCE_MO_60_TESS.Prt"
        )
        return read.PrtReader().read_monthly(result_data)

    @_pt.fixture
    def hourly_data(self):
        """Load hourly test data."""
        result_data = const.DATA_FOLDER / "plotters/data/Src_Hr.Prt"
        return read.PrtReader().read_hourly(result_data)

    @_pt.fixture
    def comparison_data(self):
        path_to_json = (
            const.DATA_FOLDER
            / "plotters/scatter-compare-plot/comparison_data.json"
        )
        return _pd.read_json(path_to_json)

    def assert_plots_match(self, actual_file, expected_file, tolerance=0.001):
        """Compare two plot images for equality."""
        if self.SKIP_PLOT_COMPARISON:
            _pt.skip(
                "Plot comparison temporarily disabled during development"
            )
        assert (
            _mpltc.compare_images(
                str(expected_file), str(actual_file), tol=tolerance
            )
            is None
        )

    def test_create_stacked_bar_chart_for_monthly(self, monthly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plotters/stacked-bar-chart/expected.png"
        )
        actual_file = (
            const.DATA_FOLDER / "plotters/stacked-bar-chart/actual.png"
        )
        columns = [
            "QSnk60PauxCondSwitch_kW",
            "QSnk60dQ",
            "QSnk60P",
            "QSnk60PDhw",
            "QSnk60dQlossTess",
            "QSnk60qImbTess",
        ]

        # Execute
        fig, _ = plot.stacked_bar_chart(monthly_data, columns, xlabel="")
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_stacked_bar_chart_for_monthly_cmap(self, monthly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plotters/stacked-bar-chart/expected_cmap.png"
        )
        actual_file = (
            const.DATA_FOLDER / "plotters/stacked-bar-chart/actual_cmap.png"
        )
        columns = [
            "QSnk60PauxCondSwitch_kW",
            "QSnk60dQ",
            "QSnk60P",
            "QSnk60PDhw",
            "QSnk60dQlossTess",
            "QSnk60qImbTess",
        ]

        # Execute
        fig, _ = plot.stacked_bar_chart(
            monthly_data, columns, xlabel="", cmap=None
        )
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_line_plot_for_hourly(self, hourly_data):
        # Setup
        expected_fig = const.DATA_FOLDER / "plotters/line-plot/expected.png"
        actual_fig = const.DATA_FOLDER / "plotters/line-plot/actual.png"
        columns = ["QSrc1TIn", "QSrc1TOut"]

        # Execute
        fig, _ = plot.line_plot(hourly_data, columns, xlabel="")
        fig.savefig(actual_fig)

        # Assert
        self.assert_plots_match(actual_fig, expected_fig)

    def test_create_line_plot_for_hourly_cmap(self, hourly_data):
        # Setup
        expected_fig = (
            const.DATA_FOLDER / "plotters/line-plot/expected_cmap.png"
        )
        actual_fig = const.DATA_FOLDER / "plotters/line-plot/actual_cmap.png"
        columns = ["QSrc1TIn", "QSrc1TOut"]

        # Execute
        fig, _ = plot.line_plot(hourly_data, columns, xlabel="", cmap="Paired")
        fig.savefig(actual_fig)

        # Assert
        self.assert_plots_match(actual_fig, expected_fig)

    def test_create_bar_chart_for_monthly(self, monthly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plotters/bar-chart/expected.png"
        actual_file = const.DATA_FOLDER / "plotters/bar-chart/actual.png"
        columns = [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ]

        # Execute
        fig, _ = plot.bar_chart(monthly_data, columns,
                                nothing=True)  # kwargs are ignored entirely!
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_bar_chart_for_monthly_with_cmap(self, monthly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plotters/bar-chart/expected_cmap.png"
        )
        actual_file = const.DATA_FOLDER / "plotters/bar-chart/actual_cmap.png"
        columns = [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ]

        # Execute
        fig, _ = plot.bar_chart(monthly_data, columns, colormap="tab20c")
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_histogram_for_hourly(self, hourly_data):
        # Setup
        expected_file = const.DATA_FOLDER / "plotters/histogram/expected.png"
        actual_file = const.DATA_FOLDER / "plotters/histogram/actual.png"
        columns = ["QSrc1TIn"]

        # Execute
        fig, _ = plot.histogram(hourly_data, columns, ylabel="")
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_create_histogram_for_hourly_color(self, hourly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plotters/histogram/expected_color.png"
        )
        actual_file = const.DATA_FOLDER / "plotters/histogram/actual_color.png"
        columns = ["QSrc1TIn"]

        # Execute
        fig, _ = plot.histogram(hourly_data, columns, ylabel="", color="red")
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_scatter_plot_for_monthly(self, monthly_data):
        # Setup
        expected_file = (
            const.DATA_FOLDER / "plotters/scatter-plot/expected.png"
        )
        actual_file = const.DATA_FOLDER / "plotters/scatter-plot/actual.png"

        # Execute
        fig, _ = plot.scatter_plot(
            monthly_data,
            x_column="QSnk60dQlossTess",
            y_column="QSnk60dQ",
        )
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_scatter_plot_raises(self, monthly_data):
        with _pt.raises(ValueError):
            plot.scatter_plot(
                monthly_data,
                x_column="QSnk60dQlossTess",
                y_column="QSnk60dQ",
                cmap="Reds"
            )

    def test_scatter_plot_for_monthly_color(self, monthly_data):
        # Setup
        actual_file = (
            const.DATA_FOLDER / "plotters/scatter-plot/actual_color.png"
        )
        expected_file = (
            const.DATA_FOLDER / "plotters/scatter-plot/expected_color.png"
        )

        # Execute
        fig, _ = plot.scatter_plot(
            monthly_data,
            x_column="QSnk60dQlossTess",
            y_column="QSnk60dQ",
            color="red",
        )
        fig.savefig(actual_file)

        # Assert
        self.assert_plots_match(actual_file, expected_file)

    def test_energy_balance_imb_given(self, monthly_data):
        # Setup
        actual_imb_given = (
            const.DATA_FOLDER / "plotters/energy-balance/actual-imb-given.png"
        )
        expected = (
            const.DATA_FOLDER / "plotters/energy-balance/expected_given.png"
        )

        # Execute
        fig, _ = plot.energy_balance(
            monthly_data,
            q_in_columns=["QSnk60PauxCondSwitch_kW"],
            q_out_columns=["QSnk60P", "QSnk60dQlossTess", "QSnk60dQ"],
            q_imb_column="QSnk60qImbTess",
            xlabel="",
        )
        fig.savefig(actual_imb_given)

        # Assert
        self.assert_plots_match(actual_imb_given, expected)

    def test_energy_balance_imb_calculated(self, monthly_data):
        # Setup
        actual_imb_calculated = (
            const.DATA_FOLDER
            / "plotters/energy-balance/actual-imb-calculated.png"
        )
        expected = (
            const.DATA_FOLDER
            / "plotters/energy-balance/expected_calculated.png"
        )

        # Execute
        fig, _ = plot.energy_balance(
            monthly_data,
            q_in_columns=["QSnk60PauxCondSwitch_kW"],
            q_out_columns=["QSnk60P", "QSnk60dQlossTess", "QSnk60dQ"],
            xlabel="",
        )
        fig.savefig(actual_imb_calculated)

        # Assert
        self.assert_plots_match(actual_imb_calculated, expected)

    def test_energy_balance_imb_calculated_cmap(self, monthly_data):
        # Setup
        actual_imb_calculated = (
            const.DATA_FOLDER
            / "plotters/energy-balance/actual-imb-calculated_cmap.png"
        )
        expected = (
            const.DATA_FOLDER / "plotters/energy-balance/expected_cmap.png"
        )

        # Execute
        fig, _ = plot.energy_balance(
            monthly_data,
            q_in_columns=["QSnk60PauxCondSwitch_kW"],
            q_out_columns=["QSnk60P", "QSnk60dQlossTess", "QSnk60dQ"],
            xlabel="",
            cmap="Paired",
        )
        fig.savefig(actual_imb_calculated)

        # Assert
        self.assert_plots_match(actual_imb_calculated, expected)

    def test_scalar_compare_plot(self, comparison_data):
        # Setup
        actual = const.DATA_FOLDER / "plotters/scatter-compare-plot/actual.png"
        expected = (
            const.DATA_FOLDER / "plotters/scatter-compare-plot/expected.png"
        )

        # Execute
        fig, _ = plot.scalar_compare_plot(
            comparison_data,
            "VIceSscaled",
            "VIceRatioMax",
            "yearly_demand_GWh",
            "ratioDHWtoSH_allSinks",
        )
        # _plt.show()
        fig.savefig(actual)

        # Assert
        self.assert_plots_match(actual, expected)

    def test_scalar_compare_plot_cmap(self, comparison_data):
        # Setup
        actual = (
            const.DATA_FOLDER / "plotters/scatter-compare-plot/actual_cmap.png"
        )
        expected = (
            const.DATA_FOLDER
            / "plotters/scatter-compare-plot/expected_cmap.png"
        )

        # Execute
        fig, _ = plot.scalar_compare_plot(
            comparison_data,
            "VIceSscaled",
            "VIceRatioMax",
            "yearly_demand_GWh",
            "ratioDHWtoSH_allSinks",
            line_kwargs={"cmap": "viridis"},
        )
        fig.savefig(actual)

        # Assert
        self.assert_plots_match(actual, expected)

    def test_scalar_compare_plot_with_kwargs_raises(self, comparison_data):
        with _pt.raises(ValueError):
            plot.scalar_compare_plot(
                comparison_data,
                "VIceSscaled",
                "VIceRatioMax",
                "yearly_demand_GWh",
                "ratioDHWtoSH_allSinks",
                cmap="viridis",
            )

    def test_scalar_compare_plot_without_grouping_raises(self, comparison_data):
        with _pt.raises(ValueError):
            plot.scalar_compare_plot(
                comparison_data,
                "VIceSscaled",
                "VIceRatioMax",
            )

    def test_scatter_compare_plot_groupby_color_only(self, comparison_data):
        # Setup
        actual = const.DATA_FOLDER / "plotters/scatter-compare-plot/actual_color_only_with_marker.png"
        expected = (
            const.DATA_FOLDER / "plotters/scatter-compare-plot/expected_color_only_with_marker.png"
        )

        # Execute
        fig, _ = plot.scalar_compare_plot(
            comparison_data,
            "VIceSscaled",
            "VIceRatioMax",
            "yearly_demand_GWh",
            scatter_kwargs={"marker": '*'}
        )
        # _plt.show()
        fig.savefig(actual)

        # Assert
        self.assert_plots_match(actual, expected)

    def test_scatter_compare_plot_groupby_marker_only(self, comparison_data):
        # Setup
        actual = const.DATA_FOLDER / "plotters/scatter-compare-plot/actual_marker_only.png"
        expected = (
            const.DATA_FOLDER / "plotters/scatter-compare-plot/expected_marker_only.png"
        )

        # Execute
        fig, _ = plot.scalar_compare_plot(
            comparison_data,
            "VIceSscaled",
            "VIceRatioMax",
            group_by_marker="ratioDHWtoSH_allSinks",
            line_kwargs={"cmap": "seismic"}
        )
        # _plt.show()
        fig.savefig(actual)

        # Assert
        self.assert_plots_match(actual, expected)

    def test_scalar_compare_plot_other_kwargs(self, comparison_data):
        # Setup
        actual = (
            const.DATA_FOLDER / "plotters/scatter-compare-plot/actual_other_kwargs.png"
        )
        expected = (
            const.DATA_FOLDER
            / "plotters/scatter-compare-plot/expected_other_kwargs.png"
        )

        # Execute
        fig, _ = plot.scalar_compare_plot(
            comparison_data,
            "VIceSscaled",
            "VIceRatioMax",
            "yearly_demand_GWh",
            "ratioDHWtoSH_allSinks",
            line_kwargs={"cmap": "viridis", "linestyle": "--"},
            scatter_kwargs={"marker": "*", "s": 100}
        )
        fig.savefig(actual)

        # Assert
        self.assert_plots_match(actual, expected)

    def test_invalid_column_names_for_plot(self, hourly_data):
        # Setup
        columns = ["qSrc1tIn", "QSrc1Tout", "DoesNotExist"]

        # Execute
        suggestion1 = r"'qSrc1tIn' did you mean: 'QSrc1TIn', "
        suggestion2 = r"'QSrc1Tout' did you mean: 'QSrc1TOut'"
        expected_message = (
            r"Column validation failed\. Case-insensitive matches found:\n"
            + f"({suggestion1}\n{suggestion2}|{suggestion2}, \n{suggestion1[:-2]})"  # Either order
            + r"\nNo matches found for:\n'DoesNotExist'"
        )

        with _pt.raises(plot.ColumnNotFoundError, match=expected_message):
            plot.line_plot(hourly_data, columns)
