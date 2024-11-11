import os as _os
import pathlib as _pl
import tempfile as _tf

import matplotlib.testing.compare as _mpltc

import tests.pytrnsys_process.constants as const
from pytrnsys_process.plotters import MonthlyBarChart
from pytrnsys_process.readers import Reader


class TestPlotter:

    HOURLY_RESULTS = _pl.Path(__file__).parent / "data/hourly/Src_Hr.Prt"
    MONTHLY_RESULTS = (
        _pl.Path(__file__).parent
        / "data/results/sim-1/temp/ENERGY_BALANCE_MO_60_TESS.Prt"
    )

    # def test_create_bar_chart_for_hourly(self):
    #     Plotter.create_bar_chart_for_hourly(
    #         Reader.read_hourly(self.HOURLY_RESULTS),
    #         columns=["QSrc1TIn", "QSrc1TOut", "QSrc1dT"],
    #     )

    def testMplInstallation(self):
        """Checks whether Inkscape is installed correctly."""
        assert "pdf" in _mpltc.comparable_formats()
        assert "svg" in _mpltc.comparable_formats()

    def test_create_stacked_bar_chart_for_monthly(self):
        expected_file = (
            const.DATA_FOLDER / "plots/stacked-bar-chart/expected.png"
        )
        actual_file = const.DATA_FOLDER / "plots/stacked-bar-chart/actual.png"
        df = Reader.read_monthly(
            self.MONTHLY_RESULTS, starting_month=11, periods=14
        )
        columns = [
            "QSnk60PauxCondSwitch_kW",
            "QSnk60dQ",
            "QSnk60P",
            "QSnk60PDhw",
            "QSnk60dQlossTess",
            "QSnk60qImbTess",
        ]

        monthly_bar_chart = MonthlyBarChart(df)
        fig, ax = monthly_bar_chart.plot(columns)
        fig.savefig(actual_file, format="png")

        assert (
            _mpltc.compare_images(
                str(actual_file), str(expected_file), tol=0.001
            )
            is None
        )

    # def test_create_energy_balance_monthly(self):
    #     manual = False
    #
    #     df = Reader.read_monthly(self.MONTHLY_RESULTS)
    #     q_in = ["QSnk60PauxCondSwitch_kW", "QSnk60dQ"]
    #     q_out = ["QSnk60P", "QSnk60PDhw", "QSnk60dQlossTess"]
    #     imbalance = "QSnk60qImbTess"
    #
    #     fig, ax = Plotter.create_bar_chart_for_monthly(
    #         df, q_in, q_out, imbalance
    #     )
    #     if manual:
    #         _plt.show()


# TODO fix, does not work as expected :/
def compare_plots(actual_buf, expected_file, tolerance=0.001):
    with _tf.NamedTemporaryFile(suffix=".png", delete=False) as actual_file:
        actual_file.write(actual_buf.read())

        actual_file.flush()

        actual_buf.seek(0)

        actual_file_path = actual_file.name

        diff = _mpltc.compare_images(
            str(expected_file), actual_file_path, tol=tolerance
        )
        _os.remove(actual_file_path)
        return diff is None
