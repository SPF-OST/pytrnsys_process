.. _tutorial

Tutorial
========

Processing individual simulations
---------------------------------
- defining a processing step
    - available data:
        - dck: simulation.scalar or
        - monthly: simulation.monthly or
        - hourly: simulation.hourly or
        - timestep: simulation.timestep or
    - plotting routines
    - calculations using python, pandas, and numpy
    - no restrictions to using other packages
    - passing results on:
        - This should be avoided wherever possible
        - processing should be done at the level where the new data is needed.
          Unlike the previous implementation, the values required at the comparison level can be produced at the comparison level.
          (e.g. the maximum value of a given variable within the hourly data)
- running a single processing step on a single simulation
- creating a unit test for a processing step
    - we should simplify how this is done
- running a single processing step on the whole set of simulations
- running multiple processing steps on a single simulation
- running multiple processing steps on the whole set of simulations
- reusing processing steps
- the processing results

processing comparisons across simulations
-----------------------------------------
- defining a comparison step
    - available data:
        - dck: processing_results.scalar
        - monthly: processing_results.monthly
        - hourly: processing_results.hourly
        - timestep: currently not available for comparisons across simulations
- auto load only the existing data for a comparison step
- running a single comparison step
    - pass in the processing results
- running multiple comparison steps
    - pass in the processing results
- reusing comparison steps