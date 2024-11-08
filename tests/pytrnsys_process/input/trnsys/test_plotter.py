import pathlib as _pl

from pytrnsys_process.input.trnsys.Plotter import Plotter
from pytrnsys_process.input.trnsys.Reader import Reader


class TestPlotter:

    HOURLY_RESULTS = _pl.Path(__file__).parent / "data/hourly/Src_Hr.Prt"

    def test_create_bar_chart_for_hourly(self):
        Plotter.create_bar_chart_for_hourly(
            Reader.read_hourly(self.HOURLY_RESULTS)
        )
        print("help")
