"""
.. _tutorial_individual_sims:
=================================
Processing Individual Simulations
=================================

This is an introduction to the processing API. For a more in-depth view,
please refer to the API docs :py:mod:`pytrnsys_process.api`

"""

# %%
# Introduction to processing individual simulations
# =================================================
# First, let's add the required imports to the top of the script.

import pathlib as _pl

from pytrnsys_process import api


# %%
# Defining a processing step
# --------------------------
# This step will use the specified columns to plot a bar chart using the monthly data.
# The Simulation object will be provided by the processing function which we will call later.


def plot_monthly_bar_chart(simulation: api.Simulation):
    columns_to_plot = ["QSnk60P", "QSnk60PauxCondSwitch_kW"]
    fig, _ = api.bar_chart(
        simulation.monthly,
        columns_to_plot,
    )
    fig.show()


# %%
# Creating multiple processing steps
# ----------------------------------
# It makes sense to split your plots into multiple steps.
# If one step fails, the others will continue to run.
# Let's define another step that creates a line plot using hourly data.
# We can customize the plot further using the `figure <https://matplotlib.org/stable/api/figure_api.html>`_
# and `axes <https://matplotlib.org/stable/api/axes_api.html>`_ objects returned by the plot function.


def plot_hourly_line_plot(simulation: api.Simulation):
    columns_to_plot = ["QSrc1TIn", "QSrc1TOut"]
    fig, ax = api.line_plot(simulation.hourly, columns_to_plot)
    ax.set_ylabel("In/Out")
    ax.set_xlabel("Timeline")
    fig.show()


# %%
# Running the processing steps
# ----------------------------
# At the end of the script, we define our entry point
# and specify which processing steps we would like to run.
# We need to pass the path to the simulation files
# and the processing steps we defined above
# to the processing function.

if __name__ == "__main__":
    path_to_sim = _pl.Path(
        "../data/results/sim-1"
    )
    sim = api.process_single_simulation(
        path_to_sim, [plot_monthly_bar_chart, plot_hourly_line_plot]
    )
    # sphinx_gallery_start_ignore
    plot_monthly_bar_chart(sim)
    plot_hourly_line_plot(sim)
# sphinx_gallery_end_ignore
