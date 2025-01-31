.. _overview:

Overview of pytrnsys processing
====

- What is the point of the package?
    - Providing processing tools for (py-)trnsys users.
    - Simplify common tasks, while
    - using Python, Pandas, and Matplotlib to provide unrestricted costumization.

- What are its main features?
    - Giving easy access to trnsys simulation data.
    - Defining processing steps in python for both single simulations and for comparisons across simulations.
    - Providing simpler interfaces to common plots.
    - Returning Matplotlib Figure and Axis handles for unrestricted costumization.


- What is the birds-eye-view experience of the package?
    - single simulation processing and across simulation processing
            - simulation steps and comparison steps
            - steps that fail will be logged and processing will continue
            - except when a critical error occurs
    - 4 ways of handling single simulation and 2 of handling across simulation

    - processing should be done at the level where the new data is needed.
          Unlike the previous implementation, the values required at the comparison level can be produced at the comparison level.
          (e.g. the maximum value of a given variable within the hourly data)
