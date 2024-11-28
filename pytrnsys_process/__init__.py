"""
pytrnsys_process package for processing TRNSYS simulation results.

This package provides tools and utilities for analyzing and processing
TRNSYS simulation output data.
"""

__version__ = "1.0.0"

from pytrnsys_process.plotting.plot_wrappers import (
    bar_chart,
    line_plot,
    stacked_bar_chart,
)
from pytrnsys_process.process_batch import (
    process_single_simulation,
    process_whole_result_set,
    process_whole_result_set_parallel,
)

__all__ = [
    "line_plot",
    "bar_chart",
    "stacked_bar_chart",
    "process_whole_result_set_parallel",
    "process_single_simulation",
    "process_whole_result_set",
]
