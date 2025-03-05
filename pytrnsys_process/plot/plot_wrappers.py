"""Plotting wrappers to provide a simplified interface to the User, while allow development of reusable OOP structures.

Note
____
    Many of these plotting routines do not add labels and legends.
    This should be done using the figure and axis handles afterwards.
"""

import typing as _tp
from collections import abc as _abc

import matplotlib.pyplot as _plt
import pandas as _pd

from pytrnsys_process import config as conf
from pytrnsys_process.plot import plotters as pltrs


def line_plot(
    df: _pd.DataFrame,
    columns: list[str],
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a line plot using the provided DataFrame columns.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments are documented in
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.line_plot(simulation.hourly, ["QSrc1TIn", "QSrc1TOut"])
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
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a bar chart with multiple columns displayed as grouped bars.
    The **kwargs are currently not passed on.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.bar_chart(simulation.monthly, ["QSnk60P","QSnk60PauxCondSwitch_kW"])
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
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Bar chart with stacked bars

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.stacked_bar_chart(simulation.monthly, ["QSnk60P","QSnk60PauxCondSwitch_kW"])
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
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    bins: int = 50,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a histogram from the given DataFrame columns.

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    columns: list of str
        names of columns to plot

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    bins: int
        number of histogram bins to be used

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.histogram(simulation.hourly, ["QSrc1TIn"], ylabel="")
    """
    _validate_column_exists(df, columns)
    plotter = pltrs.Histogram(bins)
    return plotter.plot(
        df, columns, use_legend=use_legend, size=size, **kwargs
    )


def energy_balance(
    df: _pd.DataFrame,
    q_in_columns: list[str],
    q_out_columns: list[str],
    q_imb_column: _tp.Optional[str] = None,
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a stacked bar chart showing energy balance with inputs, outputs and imbalance.
    This function creates an energy balance visualization where:

    - Input energies are shown as positive values
    - Output energies are shown as negative values
    - Energy imbalance is either provided or calculated as (sum of inputs + sum of outputs)

    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    q_in_columns: list of str
        column names representing energy inputs

    q_out_columns: list of str
        column names representing energy outputs

    q_imb_column: list of str, optional
        column name containing pre-calculated energy imbalance

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        >>> api.energy_balance(
        >>> simulation.monthly,
        >>> q_in_columns=["QSnk60PauxCondSwitch_kW"],
        >>> q_out_columns=["QSnk60P", "QSnk60dQlossTess", "QSnk60dQ"],
        >>> q_imb_column="QSnk60qImbTess",
        >>> xlabel=""
        >>> )
    """
    all_columns_vor_validation = (
        q_in_columns
        + q_out_columns
        + ([q_imb_column] if q_imb_column is not None else [])
    )
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


# pylint: disable=too-many-arguments
def scatter_plot(
    df: _pd.DataFrame,
    x_column: str,
    y_column: str,
    group_by_color: str | None = None,
    group_by_marker: str | None = None,
    use_legend: bool = True,
    size: tuple[float, float] = conf.PlotSizes.A4.value,
    **kwargs: _tp.Any,
) -> tuple[_plt.Figure, _plt.Axes]:
    """
    Create a scatter plot with up to two grouping variables.
    This visualization allows simultaneous analysis of:

    - Numerical relationships between x and y variables
    - Categorical grouping through color encoding
    - Secondary categorical grouping through marker styles

    Note
    ____
    The way to changing colors depends on how this function is used.
    Categorical grouping -> use eg: cmap="viridis"
    No grouping          -> use eg: color="red"


    Parameters
    __________
    df : pandas.DataFrame
        the dataframe to plot

    x_column: str
        coloumn name for x-axis values

    y_column: str
        coloumn name for y-axis values

    group_by_color: str, optional
        column name for color grouping

    group_by_marker: str, optional
        column name for marker style grouping

    use_legend: bool, default 'True'
        whether to show the legend or not

    size: tuple of (float, float)
        size of the figure (width, height)

    **kwargs :
        Additional keyword arguments to pass on to
        :meth:`pandas.DataFrame.plot`.

    Returns
    _______
    tuple of (:class:`matplotlib.figure.Figure`, :class:`matplotlib.axes.Axes`)

    Examples
    ________
    .. plot::
        :context: close-figs

        Simple scatter plot

        >>> api.scatter_plot(
        ...     simulation.monthly, x_column="QSnk60dQlossTess", y_column="QSnk60dQ"
        ... )

    .. plot::
        :context: close-figs

        Compare plot

        >>> api.scatter_plot(
        ...     comparison_data,
        ...     "VIceSscaled",
        ...     "VIceRatioMax",
        ...     "yearly_demand_GWh",
        ...     "ratioDHWtoSH_allSinks",
        ... )


    """
    columns_to_validate = [x_column, y_column]
    if group_by_color:
        columns_to_validate.append(group_by_color)
    if group_by_marker:
        columns_to_validate.append(group_by_marker)
    _validate_column_exists(df, columns_to_validate)
    df = df[columns_to_validate]
    plotter = pltrs.ScatterPlot()
    return plotter.plot(
        df,
        columns=[x_column, y_column],
        group_by_color=group_by_color,
        group_by_marker=group_by_marker,
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

    Parameters
    __________
        df: DataFrame to check
        columns: Sequence of column names to validate

    Raises
    ______
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
        parts.append(
            f"Case-insensitive matches found:\n{', \n'.join(suggestions)}\n"
        )
    if not_found:
        parts.append(f"No matches found for:\n{', \n'.join(not_found)}")

    error_msg = "Column validation failed. " + "".join(parts)
    raise ColumnNotFoundError(error_msg)


class ColumnNotFoundError(Exception):
    """This exception is raised when given column names are not available in the dataframe"""
