import typing as _tp
from abc import abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd

import pytrnsys_process.headers as h


# TODO: provide A4 and half A4 plots to test sizes in latex # pylint: disable=fixme
# TODO: provide height as input for plot?  # pylint: disable=fixme
# TODO: deal with legends (curve names, fonts, colors, linestyles) # pylint: disable=fixme
# TODO: clean up old stuff by refactoring # pylint: disable=fixme
# TODO: make issue for docstrings of plotting # pylint: disable=fixme


@dataclass
class ChartBase(h.HeaderValidationMixin):
    X_LABEL = ""
    Y_LABEL = ""
    TITLE = ""
    COLOR_MAP = "viridis"
    SIZE_A4 = (7.8, 3.9)
    SIZE_A4_HALF = (3.8, 3.9)
    DATE_FORMAT = "%b %Y"
    LABEL_FONT_SIZE = 10
    LEGEND_FONT_SIZE = 8
    TITLE_FONT_SIZE = 12

    def configure(self, ax: _plt.Axes) -> _plt.Axes:
        ax.set_xlabel(self.X_LABEL, fontsize=self.LABEL_FONT_SIZE)
        ax.set_ylabel(self.Y_LABEL, fontsize=self.LABEL_FONT_SIZE)
        ax.set_title(self.TITLE, fontsize=self.TITLE_FONT_SIZE)
        _plt.tight_layout()
        return ax

    def plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        **kwargs,
    ) -> _plt.Figure:
        return self._do_plot(df, columns, **kwargs)

    # TODO: Test validation # pylint: disable=fixme
    def plot_with_column_validation(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        headers: h.Headers,
        **kwargs,
    ) -> _plt.Figure:
        """Base plot method with header validation.

        Args:
            df: DataFrame containing the data to plot
            columns: List of column names to plot
            headers: Headers instance for validation
            **kwargs: Additional plotting arguments

        Raises:
            ValueError: If any columns are missing from the headers index
        """
        # TODO: Might live somewhere else in the future # pylint: disable=fixme
        is_valid, missing = self.validate_headers(headers, columns)
        if not is_valid:
            missing_details = []
            for col in missing:
                missing_details.append(f"'{col}' not found in any files")
            raise ValueError(
                "The following columns are not available in the headers index:\n"
                + "\n".join(missing_details)
            )

        return self._do_plot(df, columns, **kwargs)

    @abstractmethod
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        """Implement actual plotting logic in subclasses"""


class StackedBarChart(ChartBase):

    # def plot(self, columns: list[str]) -> Tuple[_plt.Figure | None, _plt.Axes]:
    #     # TODO: deal with datetime formatting without pandas defaults  # pylint: disable=fixme
    #     df_for_plotting = self.df
    #     df_for_plotting.index = [
    #         timestamp.strftime(self.DATE_FORMAT)
    #         for timestamp in df_for_plotting.index
    #     ]
    #     self.df[columns].plot(
    #         kind=self.PLOT_KIND,
    #         stacked=True,
    #         ax=self.ax,
    #         colormap=self.COLOR_MAP,
    #     )
    #     self.configure()
    #     return self.fig, self.ax

    # TODO: Add colormap support # pylint: disable=fixme
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = ChartBase.SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        """The matplot date formatter does not work when using df.plot func.
        This is an example to plot a stacked bar chart without df.plot"""
        fig, ax = _plt.subplots(figsize=size)
        x = df.index
        bottom = _np.zeros(len(df.index))
        for col in columns:
            ax.bar(x, df[col], label=col, bottom=bottom, width=0.35)
            bottom += df[col]
        if use_legend:
            ax.legend()
        # ax.set_xticklabels(
        #     _pd.to_datetime(df.index).strftime(self.DATE_FORMAT)
        # )
        self.configure(ax)
        return fig

    # TODO Idea for what an energy balance plot method could look like # pylint: disable=fixme
    @staticmethod
    def create_energy_balance_monthly(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        imbalance_column: str,
    ) -> _tp.Tuple[_plt.Figure, _plt.Axes]:
        raise NotImplementedError


class BarChart(ChartBase):

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = ChartBase.SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        """Creates a bar chart with multiple columns displayed as grouped bars.

        Args:
            df: DataFrame containing the data to plot
            columns: List of column names to plot as bars
            use_legend: Whether to show the legend
            size: Figure size tuple (width, height)

        Returns:
            matplotlib Figure object

        The bars for each column are grouped together, with each group centered on the x-tick.
        The bars within a group are positioned side-by-side with a small gap between them.
        The x-axis shows the datetime index formatted according to self.DATE_FORMAT.
        """
        fig, ax = _plt.subplots(figsize=size)
        x = _np.arange(len(df.index))
        width = 0.8 / len(columns)

        for i, col in enumerate(columns):
            ax.bar(x + i * width, df[col], width, label=col)

        if use_legend:
            ax.legend()

        ax.set_xticks(x + width * (len(columns) - 1) / 2)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(self.DATE_FORMAT)
        )
        ax.tick_params(axis="x", labelrotation=90)
        self.configure(ax)
        return fig


class LinePlot(ChartBase):

    PLOT_KIND = "line"

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = ChartBase.SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        fig, ax = _plt.subplots(figsize=size)
        ax = self.configure(ax)
        plot_kwargs = {
            "kind": self.PLOT_KIND,
            "colormap": self.COLOR_MAP,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        df[columns].plot(**plot_kwargs)
        return fig


class Histogram(ChartBase):
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = ChartBase.SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        fig, ax = _plt.subplots(figsize=size)
        ax = self.configure(ax)
        plot_kwargs = {
            "kind": "hist",
            "colormap": self.COLOR_MAP,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        df[columns].plot(**plot_kwargs)
        return fig

class ScatterPlot(ChartBase):
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = ChartBase.SIZE_A4,
        **kwargs: _tp.Any,
    ) -> _plt.Figure:
        fig, ax = _plt.subplots(figsize)
        ax = self.configure
        pass
