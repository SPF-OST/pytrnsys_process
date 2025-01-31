.. _iterative_workflow

Iterative workflow when developing the simulations, parametric studies, and processing
=================================================================
This document describes a recommended way of using pytrnsys and processing together to develop simulations
and parametric studies.
Here we focus on using processing the increase the learning

Iterate between developing the simulation and the processing
------------------------------------------------------------
- example: new component with new values being printed.
    - processing should be done at the level where the new data is needed.
          Unlike the previous implementation, the values required at the comparison level can be produced at the comparison level.
          (e.g. the maximum value of a given variable within the hourly data)
    - run a single processing step on a single simulation
    - create processing step for results the component (ddck) spit out.
    - iterative change the component and the processing step to maximize feedback when developing the component
    - make a unit test for the comparison step ny saving the smallest required dataset
- repeat for all components
- repeat for control
- run all processing steps on a single simulation

Creating a first parametric study
--------------------------------
- short simulation time to prepare all cases
- run all processing steps on the parametric study results

Iterate on the comparison steps
    - get all the data in debug mode
        - as soon as you know which specific data is needed in the step, save this data to file
        - processing should be done at the level where the new data is needed.
              Unlike the previous implementation, the values required at the comparison level can be produced at the comparison level.
              (e.g. the maximum value of a given variable within the hourly data)
    - use this data and the debugger to develop the comparison step
    - make a unit test for the comparison step using the saved data