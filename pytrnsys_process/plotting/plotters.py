import typing as _tp
from abc import abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd

import pytrnsys_process.constants as const
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
    ) -> tuple[_plt.Figure, _plt.Axes]:
        return self._do_plot(df, columns, **kwargs)

    # TODO: Test validation # pylint: disable=fixme
    def plot_with_column_validation(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        headers: h.Headers,
        **kwargs,
    ) -> tuple[_plt.Figure, _plt.Axes]:
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
                missing_details.append(col)
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
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        """Implement actual plotting logic in subclasses"""


class StackedBarChart(ChartBase):

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(figsize=size)
        plot_kwargs = {
            "stacked": True,
            "colormap": self.COLOR_MAP,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        ax = df[columns].plot.bar(**plot_kwargs)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(self.DATE_FORMAT)
        )
        ax = self.configure(ax)

        return fig, ax

    # TODO: Add colormap support # pylint: disable=fixme
    # def _do_plot(
    #     self,
    #     df: _pd.DataFrame,
    #     columns: list[str],
    #     use_legend: bool = True,
    #     size: tuple[float, float] = const.PlotSizes.A4.value,
    #     **kwargs: _tp.Any,
    # ) -> _plt.Figure:
    #     """The matplot date formatter does not work when using df.plot func.
    #     This is an example to plot a stacked bar chart without df.plot"""
    #     fig, ax = _plt.subplots(figsize=size)
    #     x = _np.arange(len(df.index))
    #     bottom = _np.zeros(len(df.index))
    #     for col in columns:
    #         ax.bar(x, df[col], label=col, bottom=bottom, width=0.35)
    #         bottom += df[col]
    #     if use_legend:
    #         ax.legend()
    #     ax.set_xticks(x)
    #     ax.set_xticklabels(
    #         _pd.to_datetime(df.index).strftime(self.DATE_FORMAT)
    #     )
    #     self.configure(ax)
    #     return fig

    # TODO Idea for what an energy balance plot method could look like # pylint: disable=fixme
    @staticmethod
    def create_energy_balance_monthly(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        imbalance_column: str,
    ) -> _tp.Tuple[_plt.Figure, _plt.Axes]:
        raise NotImplementedError  # pragma: no cover - has not been implemented yet


class BarChart(ChartBase):

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
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
        return fig, ax


class LinePlot(ChartBase):

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(figsize=size)
        plot_kwargs = {
            "colormap": self.COLOR_MAP,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        df[columns].plot.line(**plot_kwargs)
        ax = self.configure(ax)
        return fig, ax


@dataclass
class Histogram(ChartBase):
    bins: int = 50

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(figsize=size)
        plot_kwargs = {
            "colormap": self.COLOR_MAP,
            "legend": use_legend,
            "ax": ax,
            "bins": self.bins,
            **kwargs,
        }
        df[columns].plot.hist(**plot_kwargs)
        ax = self.configure(ax)
        return fig, ax


class ScatterPlot(ChartBase):
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(figsize=size)
        # TODO: cleanup the other Plotters to remove the stringy dictionary.
        df[columns].plot.scatter(colormap=self.COLOR_MAP, legend=use_legend, ax=ax, **kwargs)
        ax = self.configure(ax)
        return fig, ax
