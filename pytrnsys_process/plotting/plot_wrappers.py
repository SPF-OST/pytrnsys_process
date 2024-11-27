import typing as _tp

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process.plotting import plotters as pltrs


def line_plot(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = pltrs.LinePlot.SIZE_A4,
        **kwargs: _tp.Any,
) -> _plt.Figure:
    """Create a line plot from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments passed to pandas plot()

    Returns:
        matplotlib Figure object
    """
    plotter = pltrs.LinePlot()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def bar_chart(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = pltrs.BarChart.SIZE_A4,
        **kwargs: _tp.Any,
) -> _plt.Figure:
    """Create a bar chart with multiple columns displayed as grouped bars.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot as bars
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments

    Returns:
        matplotlib Figure object
    """
    plotter = pltrs.BarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def stacked_bar_chart(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = pltrs.StackedBarChart.SIZE_A4,
        **kwargs: _tp.Any,
) -> _plt.Figure:
    """Create a stacked bar chart from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments

    Returns:
        matplotlib Figure object
    """
    plotter = pltrs.StackedBarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )
