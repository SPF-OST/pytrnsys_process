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
    ax.set_xlabel(
        plot_settings.x_label, fontsize=plot_settings.label_font_size
    )
    ax.set_ylabel(
        plot_settings.y_label, fontsize=plot_settings.label_font_size
    )
    ax.set_title(plot_settings.title, fontsize=plot_settings.title_font_size)
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
class ScatterComparePlotter(ChartBase):
    """Handles comparative scatter plots with dual grouping by color and markers."""

    def _do_plot(
            self,
            df: _pd.DataFrame,
            columns: list[str],
            use_legend: bool = True,
            size: tuple[float, float] = const.PlotSizes.A4.value,
            group_by_column_names: _tp.Optional[tuple[str, str]] = None,
            **kwargs: _tp.Any,
    ) -> tuple[_plt.Figure, _plt.Axes]:
        if len(columns) != 2:
            raise ValueError(
                "ScatterComparePlotter requires exactly 2 columns (x and y)"
            )
        if not group_by_column_names or len(group_by_column_names) != 2:
            raise ValueError(
                "group_by_column_names must be a tuple of two column names"
            )

        x_column, y_column = columns
        fig, ax = _plt.subplots(figsize=size)

        # Grouping and style mapping
        df_grouped = df.groupby(list(group_by_column_names))
        group1_values = sorted(df[group_by_column_names[0]].unique())
        group2_values = sorted(df[group_by_column_names[1]].unique())

        # Color and marker mapping
        cmap = _plt.cm.get_cmap(plot_settings.color_map, len(group1_values))
        color_map = {val: cmap(i) for i, val in enumerate(group1_values)}
        marker_map = dict(zip(group2_values, plot_settings.markers))

        # Plot each group
        for (group1_val, group2_val), group in df_grouped:
            sorted_group = group.sort_values(x_column)
            color = color_map[group1_val]
            marker = marker_map[group2_val]

            ax.plot(
                sorted_group[x_column],
                sorted_group[y_column],
                color=color,
                marker=marker,
                linestyle="-",
                alpha=0.5,
            )

        # Legend creation
        if use_legend:
            self._create_legends(
                ax, color_map, marker_map, group_by_column_names
            )

        return fig, ax

    def _create_legends(self, ax, color_map, marker_map, group_names):
        # Color legend (group 1)
        color_handles = [
            _plt.Line2D([], [], color=color, linestyle="-", label=label)
            for label, color in color_map.items()
        ]
        color_legend = ax.legend(
            handles=color_handles,
            title=group_names[0],
            bbox_to_anchor=(1, 1),
            loc="upper left",
            alignment="left",
            fontsize=plot_settings.legend_font_size,
        )
        ax.add_artist(color_legend)

        # Marker legend (group 2)
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
        ]
        ax.legend(
            handles=marker_handles,
            title=group_names[1],
            bbox_to_anchor=(1, 0.7),
            loc="upper left",
            alignment="left",
            fontsize=plot_settings.legend_font_size,
        )
