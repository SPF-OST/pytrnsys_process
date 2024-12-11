import typing as _tp

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import constants as const
from pytrnsys_process.plotting import plotters as pltrs


def line_plot(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a line plot from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments passed to pandas plot()

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> from matplotlib import pyplot as _plt
        >>>
        >>> def create_line_plot(simulation: api.Simulation):
        >>>     fig, ax = api.line_plot(simulation.hourly, columns=['var1', 'var2'])
        >>>     # Customize the plot using the returned axes object:
        >>>     ax.set_xlabel('Time')
        >>>     ax.set_ylabel('Value')
        >>>     ax.set_title('My Plot')
        >>>     ax.grid(True)
        >>>     _plt.show()
        >>>
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        >>>     create_line_plot,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html
    """
    plotter = pltrs.LinePlot()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def bar_chart(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    # TODO: add description of visual grouping of bars with increasing number of columns. #pylint: disable=fixme
    """Create a bar chart with multiple columns displayed as grouped bars.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot as bars
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> def create_bar_chart(simulation: api.Simulation):
        >>>     fig, ax = api.bar_chart(simulation.monthly, columns=['var1', 'var2'])
        >>>     # Customize the plot using the returned axes object:
        >>>     ax.set_xlabel('Time')
        >>>     ax.set_ylabel('Value')
        >>>     ax.set_title('My Plot')
        >>>     ax.grid(True)
        >>>
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        >>>     create_bar_chart,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.bar.html
    """
    plotter = pltrs.BarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def stacked_bar_chart(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a stacked bar chart from the given DataFrame columns.
    - See pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.bar.html

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> def create_stacked_bar_chart(simulation: api.Simulation):
        >>>     fig, ax = api.stacked_bar_chart(simulation.monthly, columns=['var1', 'var2', 'var3'])
        >>>     # Customize the plot using the returned axes object:
        >>>     ax.set_xlabel('Time')
        >>>     ax.set_ylabel('Value')
        >>>     ax.set_title('My Plot')
        >>>     ax.grid(True)
        >>>
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        >>>     create_stacked_bar_chart,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    """
    plotter = pltrs.StackedBarChart()
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def histogram(
        df: _pd.DataFrame,
        columns: list[str],
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        bins: int = 50,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a histogram from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        bins: Number of bins to use in the histogram (default: 50)
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> def create_histogram(simulation: api.Simulation):
        >>>     fig, ax = api.histogram(simulation.hourly, columns=['var1', 'var2'])
        >>>     # Customize the plot using the returned axes object:
        >>>     ax.set_xlabel('Value')
        >>>     ax.set_ylabel('Frequency')
        >>>     ax.set_title('My Histogram')
        >>>     ax.grid(True)
        >>>
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        >>>     create_histogram,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.hist.html
    """
    plotter = pltrs.Histogram(bins)
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def scatter_plot(
        df: _pd.DataFrame,
        columns: list[str],
        x_column: str,
        y_column: str,
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a scatter plot from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
        columns: List of column names to plot
        x_column: Name of the column to use for x-axis values
        y_column: Name of the column to use for y-axis values
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> def create_scatter_plot(simulation: api.Simulation):
        >>>     fig, ax = api.scatter_plot(
        ...         simulation.hourly,
        ...         columns=["var1", "var2", "var3"],
        ...         x_column="var1",
        ...         y_column="var2",
        ...     )
        >>>     # Customize the plot using the returned axes object:
        >>>     ax.set_xlabel('Time')
        >>>     ax.set_ylabel('Value')
        >>>     ax.set_title('My Scatter Plot')
        >>>     ax.grid(True)
        >>>
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        >>>     create_scatter_plot,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.scatter.html
    """
    plotter = pltrs.ScatterPlot()
    return plotter.plot(
        df,
        columns,
        use_legend=use_legend,
        size=size,
        x=x_column,
        y=y_column,
        **kwargs,
    )
