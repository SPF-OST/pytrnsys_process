.. _get_data_into_system:

*******************************
How to Get Data into the System
*******************************

This guide explains the different ways to read data into the system.
Important to know is that the first time you read in a Simulation,
the raw files are read and after that a pickle file is created.
So the next time instead of the raw files we will read in the pickle,
which is much faster.

After rerunning your simulation(s) it is important to re-read the raw files.
This is done as follows:

.. code-block:: python

    api.global_settings.reader.force_reread_prt = True

Do not forget to turn this off again for faster data loading.

Common Arguments
________________

The following arguments are commonly used across different data loading functions:

- ``results_folder``: A :class:`pathlib.Path` object containing the path to all simulations you want to process.
- ``processing_scenarios``: A single processing step or an array of steps.
- ``comparison_scenario``: A single comparison_step or an array of steps.

Reading in a Single Simulation
______________________________

- ``sim_folder``: A :class:`pathlib.Path` object containing the path to your simulation results.

.. code-block:: python

    simulation = api.process_single_simulation(sim_folder, processing_scenarios)

Reading in Multiple Simulations
_______________________________

.. code-block:: python

    simulations_data = api.process_whole_result_set(results_folder, processing_scenarios)

Reading in Multiple Simulations in Parallel
___________________________________________

- ``max_workers``: An optional argument that defines how many processors the function should use.
  If nothing is provided it will use as many as it can.

.. code-block:: python

    simulations_data = api.process_whole_result_set_parallel(results_folder, processing_scenarios, max_workers=4)

For Comparison
______________

.. code-block:: python

    api.do_comparison(comparison_scenario, results_folder)


After calling :meth:`pytrnsys_process.api.process_whole_result_set` or
:meth:`pytrnsys_process.api.process_whole_result_set_parallel`.
You can use the returned :class:`pytrnsys_process.api.SimulationsData` object
and pass it to the :meth:`pytrnsys_process.api.do_comparison` function.

.. code-block:: python

    api.do_comparison(comparison_scenario, simulations_data)
