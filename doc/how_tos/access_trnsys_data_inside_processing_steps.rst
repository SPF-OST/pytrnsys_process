.. _do_calculations_on_data:

*************************************************
How to Access TRNSYS Data Inside Processing Steps
*************************************************

TRNSYS data comes in many shapes.
Scalars are available in the *.dck* file and results come in the form of *monthly*, *hourly*, and *timestep* values.

To access this data, there is a slight difference between *processing steps for individual simulations* and *comparison steps*.
Individual processing steps only have access to data from a single simulation and comparison steps have access to data from all the provided simulations.

Accessing data in an individual simulation step
_______________________________________________

Individual simulation steps can be defined as follows:

.. code-block:: python

    def step_1(simulation):


During processing a :class:`pytrnsys_process.api.Simulation` object will automatically be passed into this step.
It contains a :class:`pandas.DataFrame` objects for the *hourly*, *monthly*, and *timestep* data.
For individual simulation steps, the scalar data is also a *DataFrame* with a single row.

Accessing the data thus reduces to:

.. code-block:: python

    def processing_step(simulation):
        var_1_monthly_column = simulation.monthly["QSnk60P"]
        var_1_hourly_column = simulation.hourly["QSnk60P"]
        var_1_timestep_column = simulation.step["QSnk60P"]
        var_2_scalar_value = simulation.scalar["ratioDHWtoSH_allSinks"]

Here, single values are returned when accessing *simulation.scalar*, whereas the other *DataFrames* return a column of data.



Accessing Data in a Comparison Step
___________________________________

The comparison step allows you to analyze data across multiple simulations.
While the same types of data are available (*scalar*, *hourly*, *monthly*, and *timestep*); the way the data is accessed is slightly different.

Comparison steps can be defined as follows:

.. code-block:: python

    def step_1(simulations_data):


During processing a :class:`pytrnsys_process.api.SimulationsData` object will automatically be passed into this comparison step.
It contains a :class:`pytrnsys_process.api.SimulationsData` object for each simulation, as well as a :class:`pandas.DataFrame' object for all the scalar data.

You can thus access the data as follows:

.. code-block:: python

    def comparison_step(simulations_data):

        var_2_column = simulations_data.scalar["ratioDHWtoSH_allSinks"]

        for sim_name, sim in simulations_data.simulations.items():
            # Get data for current simulation
            var_1_monthly_column = sim.monthly["QSnk60P"]
            var_1_hourly_column = sim.hourly["QSnk60P"]
            var_1_timestep_column = sim.step["QSnk60P"]

Accessing the scalar data here thus returns a column of data, i.e., one value for each of the simulations.
For the other data, a DataFrame can be accessed for each simulation.


Advanced data access
____________________
Pandas DataFrames provide many ways to access data.
For more information on how to use Pandas DataFrames, we refer to the `Pandas Tutorials <https://pandas.pydata.org/docs/getting_started/index.html>`_ (e.g. *How to select a subset of a table*) and `User's Guide <https://pandas.pydata.org/docs/user_guide/index.html>`_.


