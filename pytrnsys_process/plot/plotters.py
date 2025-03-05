import typing as _tp
from abc import abstractmethod
from dataclasses import dataclass

import matplotlib.pyplot as _plt
import numpy as _np
import pandas as _pd

from pytrnsys_process import config as conf

# TODO: provide A4 and half A4 plots to test sizes in latex # pylint: disable=fixme
# TODO: provide height as input for plot?  # pylint: disable=fixme
# TODO: deal with legends (curve names, fonts, colors, linestyles) # pylint: disable=fixme
# TODO: clean up old stuff by refactoring # pylint: disable=fixme
# TODO: make issue for docstrings of plotting # pylint: disable=fixme
# TODO: Add colormap support # pylint: disable=fixme


# TODO find a better place for this to live in # pylint : disable=fixme
plot_settings = conf.global_settings.plot
"Settings shared by all plots"


class ChartBase:
    cmap: str | None = None

    def plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        **kwargs,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = self._do_plot(df, columns, **kwargs)
        return fig, ax

    @abstractmethod
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        """Implement actual plotting logic in subclasses"""

    def check_for_cmap(self, kwargs, plot_kwargs):
        if "cmap" not in kwargs and "colormap" not in kwargs:
            plot_kwargs["cmap"] = self.cmap
        return plot_kwargs

    def get_cmap(self, kwargs) -> str | None:
        if "cmap" not in kwargs and "colormap" not in kwargs:
            return self.cmap

        if "cmap" in kwargs:
            return kwargs["cmap"]

        if "colormap" in kwargs:
            return kwargs["colormap"]

        raise ValueError


class StackedBarChart(ChartBase):
    cmap: str | None = "inferno_r"

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(
            figsize=size,
            layout="constrained",
        )
        plot_kwargs = {
            "stacked": True,
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)
        ax = df[columns].plot.bar(**plot_kwargs)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )

        return fig, ax


class BarChart(ChartBase):
    cmap = None

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        # TODO: deal with colors  # pylint: disable=fixme
        fig, ax = _plt.subplots(
            figsize=size,
            layout="constrained",
        )
        x = _np.arange(len(df.index))
        width = 0.8 / len(columns)

        cmap = self.get_cmap(kwargs)
        if cmap:
            cm = _plt.cm.get_cmap(cmap)
            colors = cm(_np.linspace(0, 1, len(columns)))
        else:
            colors = [None] * len(columns)

        for i, col in enumerate(columns):
            ax.bar(x + i * width, df[col], width, label=col, color=colors[i])

        if use_legend:
            ax.legend()

        ax.set_xticks(x + width * (len(columns) - 1) / 2)
        ax.set_xticklabels(
            _pd.to_datetime(df.index).strftime(plot_settings.date_format)
        )
        ax.tick_params(axis="x", labelrotation=90)
        return fig, ax


class LinePlot(ChartBase):
    cmap: str | None = None

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(
            figsize=size,
            layout="constrained",
        )
        plot_kwargs = {
            "legend": use_legend,
            "ax": ax,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)

        df[columns].plot.line(**plot_kwargs)
        return fig, ax


@dataclass()
class Histogram(ChartBase):
    bins: int = 50

    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        fig, ax = _plt.subplots(
            figsize=size,
            layout="constrained",
        )
        plot_kwargs = {
            "legend": use_legend,
            "ax": ax,
            "bins": self.bins,
            **kwargs,
        }
        self.check_for_cmap(kwargs, plot_kwargs)
        df[columns].plot.hist(**plot_kwargs)
        return fig, ax


class ScatterPlot(ChartBase):
    """Handles comparative scatter plots with dual grouping by color and markers."""

    cmap = "Paired"  # This is ignored when no categorical groupings are used.

    # pylint: disable=too-many-arguments,too-many-locals
    def _do_plot(
        self,
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = conf.PlotSizes.A4.value,
        group_by_color: str | None = None,
        group_by_marker: str | None = None,
        **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        self._validate_inputs(columns)
        x_column, y_column = columns

        if not group_by_color and not group_by_marker:
            fig, ax = _plt.subplots(
                figsize=size,
                layout="constrained",
            )
            df.plot.scatter(x=x_column, y=y_column, ax=ax, **kwargs)
            return fig, ax
        # See: https://stackoverflow.com/questions/4700614/
        # how-to-put-the-legend-outside-the-plot
        # This is required to place the legend in a dedicated subplot
        fig, (ax, lax) = _plt.subplots(
            layout="constrained",
            figsize=size,
            ncols=2,
            gridspec_kw={"width_ratios": [4, 1]},
        )
        df_grouped, group_values = self._prepare_grouping(
            df, group_by_color, group_by_marker
        )
        cmap = self.get_cmap(kwargs)
        color_map, marker_map = self._create_style_mappings(
            *group_values, cmap=cmap
        )

        self._plot_groups(
            df_grouped,
            x_column,
            y_column,
            color_map,
            marker_map,
            ax,
        )

        if use_legend:
            self._create_legends(
                lax, color_map, marker_map, group_by_color, group_by_marker
            )

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
        self,
        color_values: list[str],
        marker_values: list[str],
        cmap: str | None,
    ) -> tuple[dict[str, _tp.Any], dict[str, str]]:
        if color_values:
            cm = _plt.get_cmap(cmap, len(color_values))
            color_map = {val: cm(i) for i, val in enumerate(color_values)}
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
        lax: _plt.Axes,
        color_map: dict[str, _tp.Any],
        marker_map: dict[str, str],
        color_legend_title: str | None,
        marker_legend_title: str | None,
    ) -> None:
        lax.axis("off")

        if color_map:
            self._create_color_legend(
                lax, color_map, color_legend_title, bool(marker_map)
            )
        if marker_map:
            self._create_marker_legend(
                lax, marker_map, marker_legend_title, bool(color_map)
            )

    def _create_color_legend(
        self,
        lax: _plt.Axes,
        color_map: dict[str, _tp.Any],
        color_legend_title: str | None,
        has_markers: bool,
    ) -> None:
        color_handles = [
            _plt.Line2D([], [], color=color, linestyle="-", label=label)
            for label, color in color_map.items()
        ]

        legend = lax.legend(
            handles=color_handles,
            title=color_legend_title,
            bbox_to_anchor=(0, 0, 1, 1),
            loc="upper left",
            alignment="left",
            fontsize=plot_settings.legend_font_size,
            borderaxespad=0,
        )

        if has_markers:
            lax.add_artist(legend)

    def _create_marker_legend(
        self,
        lax: _plt.Axes,
        marker_map: dict[str, str],
        marker_legend_title: str | None,
        has_colors: bool,
    ) -> None:
        marker_position = 0.7 if has_colors else 1
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

        lax.legend(
            handles=marker_handles,
            title=marker_legend_title,
            bbox_to_anchor=(0, 0, 1, marker_position),
            loc="upper left",
            alignment="left",
            fontsize=plot_settings.legend_font_size,
            borderaxespad=0,
        )
