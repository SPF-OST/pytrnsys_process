import typing as _tp
from abc import abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd

import pytrnsys_process.constants as const
import pytrnsys_process.headers as h
from pytrnsys_process import settings as sett

# TODO: provide A4 and half A4 plots to test sizes in latex # pylint: disable=fixme
# TODO: provide height as input for plot?  # pylint: disable=fixme
# TODO: deal with legends (curve names, fonts, colors, linestyles) # pylint: disable=fixme
# TODO: clean up old stuff by refactoring # pylint: disable=fixme
# TODO: make issue for docstrings of plotting # pylint: disable=fixme
# TODO: Add colormap support # pylint: disable=fixme


# TODO find a better place for this to live in # pylint : disable=fixme
plot_settings = sett.settings.plot


def configure(ax: _plt.Axes) -> _plt.Axes:
    ax.set_xlabel(
        plot_settings.x_label, fontsize=plot_settings.label_font_size
    )
    ax.set_ylabel(
        plot_settings.y_label, fontsize=plot_settings.label_font_size
    )
    ax.set_title(plot_settings.title, fontsize=plot_settings.title_font_size)
    _plt.tight_layout()
    return ax


@dataclass
class ChartBase(h.HeaderValidationMixin):

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
            "colormap": plot_settings.color_map,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        ax = df[columns].plot.bar(**plot_kwargs)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )
        ax = configure(ax)

        return fig, ax

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
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )
        ax.tick_params(axis="x", labelrotation=90)
        configure(ax)
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
            "colormap": plot_settings.color_map,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        df[columns].plot.line(**plot_kwargs)
        ax = configure(ax)
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
            "colormap": plot_settings.color_map,
            "legend": use_legend,
            "ax": ax,
            "bins": self.bins,
            **kwargs,
        }
        df[columns].plot.hist(**plot_kwargs)
        ax = configure(ax)
        return fig, ax
