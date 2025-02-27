.. _do_calculations_on_data:

**********************************
How to Do Calculations on the Data
**********************************

This guide explains how to perform calculations on your data within different processing steps.

For Simulation Step
___________________

The simulation step allows you to perform calculations on hourly data.
Below is an example that demonstrates how to:

1. Sum values from two columns
2. Convert units from kWh to GWh
3. Store the result in a new column

.. code-block:: python

    def processing_step(simulation):
        # Define conversion factor
        kwh_to_gwh = 1e-6
        
        # Calculate sum of columns and convert units
        simulation.hourly["column_sum"] = (
            simulation.hourly[["column_1", "column_2"]].sum(axis=1) * kwh_to_gwh
        )

For Comparison Step
___________________

The comparison step allows you to analyze data across multiple simulations.
This example shows how to:

1. Iterate through simulations
2. Calculate the maximum value for a specific column
3. Store results in the scalar dataframe

.. code-block:: python

    def comparison_step(simulations_data):
        for sim_name, sim in simulations_data.simulations.items():
            # Get hourly data for current simulation
            hourly_data = sim.hourly
            
            # Calculate maximum value
            column_max = hourly_data["column_1"].max()
            
            # Store result in scalar dataframe
            simulations_data.scalar.loc[sim_name, "column_max"] = column_max






