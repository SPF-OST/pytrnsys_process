import pathlib as _pl

from pytrnsys_process.input.trnsys.plotters import MonthlyBarChart
from pytrnsys_process.input.trnsys.readers import Reader


# TODO: replace hourly file with Mo for src_*.prt  # pylint: disable=fixme
# TODO: show MM-YYYY at bottom.
# TODO: make reusable
# TODO: fix read monthly


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

    def test_create_bar_chart_for_monthly(self):
        df = Reader.read_monthly(self.MONTHLY_RESULTS, starting_month=11, periods=14)
        columns = ["QSnk60PauxCondSwitch_kW", "QSnk60dQ"]
        monthly_bar_chart = MonthlyBarChart(df)
        fig, ax  = monthly_bar_chart.plot(columns)
        fig.savefig(f"{self.MONTHLY_RESULTS.stem}.png")


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
