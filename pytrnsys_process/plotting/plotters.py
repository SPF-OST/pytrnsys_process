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


def configure(
        fig: _plt.Figure, ax: _plt.Axes
) -> tuple[_plt.Figure, _plt.Axes]:
    fig.tight_layout()
    return fig, ax


@dataclass
class ChartBase(h.HeaderValidationMixin):

    def plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        **kwargs,
    ) -> tuple[_plt.Figure, _plt.Axes]:

        fig, ax = configure(*self._do_plot(df, columns, **kwargs))
        fig.tight_layout()
        return fig, ax

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

        return fig, ax


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
        return fig, ax


@dataclass
class ScatterPlot(ChartBase):
    """Handles comparative scatter plots with dual grouping by color and markers."""

    # pylint: disable=too-many-arguments,too-many-locals
    def _do_plot(
            self,
            df: _pd.DataFrame,
            columns: list[str],
            use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
            color: str | None = None,
            marker: str | None = None,
            **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        self._validate_inputs(columns)
        x_column, y_column = columns
        fig, ax = _plt.subplots(figsize=size)

        if not color and not marker:
            df.plot.scatter(x=x_column, y=y_column, ax=ax, **kwargs)
            return fig, ax

        df_grouped, group_values = self._prepare_grouping(df, color, marker)
        color_map, marker_map = self._create_style_mappings(*group_values)

        self._plot_groups(
            df_grouped,
            x_column,
            y_column,
            color_map,
            marker_map,
            ax,
        )

        if use_legend:
            self._create_legends(ax, color_map, marker_map, color, marker)

        return fig, ax

    def _validate_inputs(
            self,
            columns: list[str],
    ) -> None:
        if len(columns) != 2:
            raise ValueError(
                "ScatterComparePlotter requires exactly 2 columns (x and y)"
            )

    def _prepare_grouping(
            self,
            df: _pd.DataFrame,
            color: str | None,
            marker: str | None,
    ) -> tuple[
        _pd.core.groupby.generic.DataFrameGroupBy, tuple[list[str], list[str]]
    ]:
        group_by = []
        if color:
            group_by.append(color)
        if marker:
            group_by.append(marker)

        df_grouped = df.groupby(group_by)

        color_values = sorted(df[color].unique()) if color else []
        marker_values = sorted(df[marker].unique()) if marker else []

        return df_grouped, (color_values, marker_values)

    def _create_style_mappings(
            self, color_values: list[str], marker_values: list[str]
    ) -> tuple[dict[str, _tp.Any], dict[str, str]]:
        if color_values:
            cmap = _plt.cm.get_cmap(plot_settings.color_map, len(color_values))
            color_map = {val: cmap(i) for i, val in enumerate(color_values)}
        else:
            color_map = {}
        if marker_values:
            marker_map = dict(zip(marker_values, plot_settings.markers))
        else:
            marker_map = {}

        return color_map, marker_map

    # pylint: disable=too-many-arguments
    def _plot_groups(
            self,
            df_grouped: _pd.core.groupby.generic.DataFrameGroupBy,
            x_column: str,
            y_column: str,
            color_map: dict[str, _tp.Any],
            marker_map: dict[str, str],
            ax: _plt.Axes,
    ) -> None:
        ax.set_xlabel(x_column, fontsize=plot_settings.label_font_size)
        ax.set_ylabel(y_column, fontsize=plot_settings.label_font_size)
        for val, group in df_grouped:
            sorted_group = group.sort_values(x_column)
            x = sorted_group[x_column]
            y = sorted_group[y_column]
            plot_args = {"color": "black"}
            scatter_args = {"marker": "None", "color": "black", "alpha": 0.5}
            if color_map:
                plot_args["color"] = color_map[val[0]]
            if marker_map:
                scatter_args["marker"] = marker_map[val[-1]]
            ax.plot(x, y, **plot_args)  # type: ignore
            ax.scatter(x, y, **scatter_args)  # type: ignore

    def _create_legends(
            self,
            ax: _plt.Axes,
            color_map: dict[str, _tp.Any],
            marker_map: dict[str, str],
            color_legend_title: str | None,
            marker_legend_title: str | None,
    ) -> None:

        if color_map:
            color_handles = [
                _plt.Line2D([], [], color=color, linestyle="-", label=label)
                for label, color in color_map.items()
            ]
            color_legend = ax.legend(
                handles=color_handles,
                title=color_legend_title,
                bbox_to_anchor=(1, 1),
                loc="upper left",
                alignment="left",
                fontsize=plot_settings.legend_font_size,
            )
            ax.add_artist(color_legend)
        if marker_map:
            marker_position = 0.7 if color_map else 1
            marker_handles = [
                _plt.Line2D(
                    [],
                    [],
                    color="black",
                    marker=marker,
                    linestyle="None",
                    label=label,
                )
                for label, marker in marker_map.items()
                if label is not None
            ]
            ax.legend(
                handles=marker_handles,
                title=marker_legend_title,
                bbox_to_anchor=(1, marker_position),
                loc="upper left",
                alignment="left",
                fontsize=plot_settings.legend_font_size,
            )
