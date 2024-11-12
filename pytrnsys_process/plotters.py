from abc import abstractmethod
from typing import Tuple

import matplotlib.dates as _mpd
import matplotlib.pyplot as _plt
import pandas as _pd


# TODO: provide A4 and half A4 plots to test sizes in latex # pylint: disable=fixme
# TODO: provide height as input for plot?  # pylint: disable=fixme
# TODO: deal with legends (curve names, fonts, colors, linestyles) # pylint: disable=fixme
# TODO: clean up old stuff by refactoring # pylint: disable=fixme
# TODO: make issue for docstrings of plotting # pylint: disable=fixme


class ChartBase:
    X_LABEL = ""
    Y_LABEL = "Energy Flows"
    TITLE = ""
    COLOR_MAP = "viridis"
    SIZE_A4 = (7.8, 3.9)
    SIZE_A4_HALF = (3.8, 3.9)
    DATE_FORMAT = "%m-%y"
    LABEL_FONT_SIZE = 10
    LEGEND_FONT_SIZE = 8
    TITLE_FONT_SIZE = 12

    # TODO: discuss if we should we use a dic or a dataclass for config values # pylint: disable=fixme
    def __init__(self, df, size=SIZE_A4):
        self.df = df
        self.fig, self.ax = _plt.subplots(figsize=size)

    def configure(self):
        self.ax.set_xlabel(self.X_LABEL, fontsize=self.LABEL_FONT_SIZE)
        self.ax.set_ylabel(self.Y_LABEL, fontsize=self.LABEL_FONT_SIZE)
        self.ax.set_title(self.TITLE, fontsize=self.TITLE_FONT_SIZE)
        _plt.tight_layout()

    @abstractmethod
    def plot(self, *args, **kwargs):
        raise NotImplementedError

    # makes no sense
    # def _plot(self, df, columns: list[str]):
    #     # TODO: check if this makes sense. # pylint: disable=fixme
    #     self.plot(df, columns)
    #     self.configure()


class MonthlyBarChart(ChartBase):

    PLOT_KIND = "bar"

    def plot(self, columns: list[str]) -> Tuple[_plt.Figure | None, _plt.Axes]:
        # TODO: deal with datetime formatting without pandas defaults  # pylint: disable=fixme
        df_for_plotting = self.df
        df_for_plotting.index = [
            timestamp.strftime(self.DATE_FORMAT) for timestamp in df_for_plotting.index
        ]
        self.df[columns].plot(
            kind=self.PLOT_KIND,
            stacked=True,
            ax=self.ax,
            colormap=self.COLOR_MAP,
        )
        self.configure()
        return self.fig, self.ax

    def plot_without_pandas( # pragma: no cover
        self, columns: list[str]
    ) -> Tuple[_plt.Figure | None, _plt.Axes]:
        """The matplot date formatter does not work when using df.plot func.
        This is an example to plot a stacked bar chart without df.plot"""
        bottom = None
        for col in columns:
            self.ax.bar(self.df.index, self.df[col], label=col, bottom=bottom)
            bottom = self.df[col] if bottom is None else bottom + self.df[col]
        self.ax.xaxis.set_major_formatter(_mpd.DateFormatter(self.DATE_FORMAT))
        self.configure()
        return self.fig, self.ax

    # TODO Idea for what an energy balance plot method could look like # pylint: disable=fixme
    @staticmethod
    def create_energy_balance_monthly(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        imbalance_column: str,
    ) -> Tuple[_plt.Figure, _plt.Axes]:
        raise NotImplementedError


class HourlyCurvePlot(ChartBase):

    PLOT_KIND = "line"

    def plot(
        self, columns: list[str], use_legend: bool = True
    ) -> Tuple[_plt.Figure | None, _plt.Axes]:
        self.df[columns].plot(
            kind=self.PLOT_KIND,
            colormap=self.COLOR_MAP,
            legend=use_legend,
            ax=self.ax,
        )
        self.configure()
        return self.fig, self.ax
