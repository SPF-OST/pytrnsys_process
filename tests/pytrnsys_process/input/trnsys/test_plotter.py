import pathlib as _pl

import matplotlib as _plt
from pytrnsys_process.input.trnsys.Plotter import Plotter
from pytrnsys_process.input.trnsys.Reader import Reader


class TestPlotter:

    HOURLY_RESULTS = _pl.Path(__file__).parent / "data/hourly/Src_Hr.Prt"
    MONTHLY_RESULTS = _pl.Path(__file__).parent / "data/results/sim-1/temp/ENERGY_BALANCE_MO_60_TESS.Prt"

    def test_create_bar_chart_for_hourly(self):
        Plotter.create_bar_chart_for_hourly(
            Reader.read_hourly(self.HOURLY_RESULTS)
        )

    def test_create_bar_chart_for_monthly(self):
        manual=False

        df = Reader.read_monthly(self.MONTHLY_RESULTS)
        columns = ["QSnk60PauxCondSwitch_kW", "QSnk60dQ"]
        # q_out = ["QSnk60P", "QSnk60PDhw", "QSnk60dQlossTess"]
        # imbalance = "QSnk60qImbTess"

        fig, ax = Plotter.create_bar_chart_for_monthly(df, columns)
        if manual:
            _plt.show()

    def test_create_energy_balance_monthly(self):
        manual=False

        df = Reader.read_monthly(self.MONTHLY_RESULTS)
        q_in = ["QSnk60PauxCondSwitch_kW", "QSnk60dQ"]
        q_out = ["QSnk60P", "QSnk60PDhw", "QSnk60dQlossTess"]
        imbalance = "QSnk60qImbTess"

        fig, ax = Plotter.create_bar_chart_for_monthly(df, q_in, q_out, imbalance)
        if manual:
            _plt.show()

