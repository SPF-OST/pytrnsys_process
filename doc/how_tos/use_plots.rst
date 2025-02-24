.. _use_plots:

*******************************
How to Use Plots
*******************************

There are multiple plots available to use in your processing steps.

Line Plot
_________

.. code-block:: python

    def step(simulation):
        api.line_plot(df=simulation.hourly, columns_to_plot=["column_1", "column_2"])


