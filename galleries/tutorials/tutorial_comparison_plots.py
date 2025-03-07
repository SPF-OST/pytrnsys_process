"""
.. _tutorial_comparison_plots:
=================================
Comparison Plots
=================================

This tutorial will guide you to creating your own comparison plots.
For a more in-depth view, please refer to the :ref:`how_tos` and the API docs :ref:`api-reference-api`

"""



# %%
# Required Imports
# ================
# First, let's add the required imports to the top of the script.

import pathlib as _pl

from pytrnsys_process import api


# %%
# Introduction to processing individual simulations
# =================================================
# First, you will need to download the
# `example data. <https://raw.githubusercontent.com/SPF-OST/pytrnsys_process/main/example_data/example_data.zip>`_
#
# Extract the data into a project folder you will use for this tutorial.
# You should end up with a folder structure looking like this.
#
# | root
# | ├─ example_data
# | ├─ tutorials
# |     ├─ tutorial_individual_sims.py
#
# For the rest of this tutorial, you should work in the last file: "tutorial_individual_sims.py"


# %%


# %%
# There are different ways you can provide data to run your comparison steps.
# Using the returned :class:`pytrnsys_process.api.SimulationsResults`

simulations_results = api.process_whole_result_set_parallel("")
