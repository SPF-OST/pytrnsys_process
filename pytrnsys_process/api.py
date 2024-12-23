"""
pytrnsys_process package for processing TRNSYS simulation results.

This package provides tools and utilities for analyzing and processing
TRNSYS simulation output data.
"""

__version__ = "0.0.1"

from pytrnsys_process.plotting.plot_wrappers import (
    bar_chart,
    line_plot,
    stacked_bar_chart,
    histogram,
    scatter_plot,
)
from pytrnsys_process.process_batch import (
    process_single_simulation,
    process_whole_result_set,
    process_whole_result_set_parallel,
)
from pytrnsys_process.process_sim.process_sim import Simulation

# ============================================================
# this lives here, because it needs to be available everywhere
from pytrnsys_process.settings import settings, Defaults

# ============================================================

from pytrnsys_process.utils import export_plots_in_configured_formats

__all__ = [
    "line_plot",
    "bar_chart",
    "stacked_bar_chart",
    "histogram",
    "scatter_plot",
    "process_whole_result_set_parallel",
    "process_single_simulation",
    "process_whole_result_set",
    "Simulation",
    "export_plots_in_configured_formats",
    "settings",
    "Defaults"
]
