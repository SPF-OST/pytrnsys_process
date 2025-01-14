import typing as _tp
from collections import abc as _abc

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
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_line_plot,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.html
    """
    _validate_column_exists(df, columns)
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
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_bar_chart,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.bar.html
    """
    _validate_column_exists(df, columns)
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
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_stacked_bar_chart,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    """
    _validate_column_exists(df, columns)
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
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_histogram,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.hist.html
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.Histogram(bins)
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def scatter_plot(
        df: _pd.DataFrame,
        x_column: str,
        y_column: str,
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a scatter plot from the given DataFrame columns.

    Args:
        df: DataFrame containing the data to plot
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
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_scatter_plot,
        >>>     )

    For additional customization options, refer to:
    - Matplotlib documentation: https://matplotlib.org/stable/api/
    - Pandas plotting: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.plot.scatter.html
    """
    _validate_column_exists(df, [x_column, y_column])
    fig, ax = _plt.subplots(figsize=size)
    columns = [x_column, y_column]
    df[columns].plot.scatter(
        legend=use_legend,
        ax=ax,
        x=x_column,
        y=y_column,
        **kwargs,
    )
    ax = pltrs.configure(ax)

    return fig, ax


def energy_balance(
        df: _pd.DataFrame,
        q_in_columns: list[str],
        q_out_columns: list[str],
        q_imb_column: _tp.Optional[str] = None,
        use_legend: bool = True,
        size: tuple[float, float] = const.PlotSizes.A4.value,
        **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """Create a stacked bar chart showing energy balance with inputs, outputs and imbalance.

    This function creates an energy balance visualization where:
    - Input energies are shown as positive values
    - Output energies are shown as negative values
    - Energy imbalance is either provided or calculated as (sum of inputs + sum of outputs)

    Args:
        df: DataFrame containing the energy data
        q_in_columns: List of column names representing energy inputs
        q_out_columns: List of column names representing energy outputs
        q_imb_column: Optional column name containing pre-calculated energy imbalance
        use_legend: Whether to show the legend
        size: Figure size tuple (width, height)
        **kwargs: Additional plotting arguments passed to the stacked bar chart

    Returns:
        Tuple of (matplotlib Figure object, matplotlib Axes object)

    Example:
        >>> from pytrnsys_process import api
        >>> def create_energy_balance(simulation: api.Simulation):
        >>>     fig, ax = api.energy_balance(
        ...         simulation.monthly,
        ...         q_in_columns=['solar_gain', 'auxiliary_power'],
        ...         q_out_columns=['thermal_losses', 'consumption'],
        ...     )
        >>>     ax.set_xlabel('Time')
        >>>     ax.set_ylabel('Energy [kWh]')
        >>>     ax.set_title('Monthly Energy Balance')
        >>>     ax.grid(True)
        >>> # run the single scenario on a single simulation
        >>> api.process_single_simulation(
        >>>     _pl.Path("path/to/single/simulation"),
        >>>     create_energy_balance,
        >>>     )
    """
    all_columns_vor_validation = q_in_columns + q_out_columns + ([q_imb_column] if q_imb_column is not None else [])
    _validate_column_exists(df, all_columns_vor_validation)

    df_modified = df.copy()

    for col in q_out_columns:
        df_modified[col] = -df_modified[col]

    if q_imb_column is None:
        q_imb_column = "Qimb"
        df_modified[q_imb_column] = df_modified[
            q_in_columns + q_out_columns
        ].sum(axis=1)

    columns_to_plot = q_in_columns + q_out_columns + [q_imb_column]

    plotter = pltrs.StackedBarChart()
    return plotter.plot(
        df_modified,
        columns_to_plot,
        use_legend=use_legend,
        size=size,
        **kwargs,
    )


def _validate_column_exists(
        df: _pd.DataFrame, columns: _abc.Sequence[str]
) -> None:
    """Validate that all requested columns exist in the DataFrame.

    Since PyTRNSYS is case-insensitive but Python is case-sensitive, this function
    provides helpful suggestions when columns differ only by case.

    Args:
        df: DataFrame to check
        columns: Sequence of column names to validate

    Raises:
        ColumnNotFoundError: If any columns are missing, with suggestions for case-mismatched names
    """
    missing_columns = set(columns) - set(df.columns)
    if not missing_columns:
        return

    # Create case-insensitive mapping of actual column names
    column_name_mapping = {col.casefold(): col for col in df.columns}

    # Categorize missing columns
    suggestions = []
    not_found = []

    for col in missing_columns:
        if col.casefold() in column_name_mapping:
            correct_name = column_name_mapping[col.casefold()]
            suggestions.append(f"'{col}' did you mean: '{correct_name}'")
        else:
            not_found.append(f"'{col}'")

    # Build error message
    parts = []
    if suggestions:
        parts.append(f"Case-insensitive matches found:\n{', \n'.join(suggestions)}\n")
    if not_found:
        parts.append(f"No matches found for:\n{', \n'.join(not_found)}")

    error_msg = "Column validation failed. " + "".join(parts)
    raise ColumnNotFoundError(error_msg)


class ColumnNotFoundError(Exception):
    """This expedition is raised when given column names are not available in the dataframe"""
