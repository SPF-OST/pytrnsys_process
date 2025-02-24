.. _add_individual_steps:

***************************
How to Add Individual Steps
***************************

Adding Processing Steps
_______________________

You can define as many processing steps as you'd like.

.. code-block:: python

    def step_1(simulation):
        pass

    def step_2(simulation):
        pass

    def step_3(simulation):
        pass

    def main():
        scenario = [step_1, step_2, step_3]

        api.process_single_simulation(path_to_sim, scenario)

        api.process_single_simulation(path_to_sim, step_1)

Adding Comparison Steps
_______________________

.. code-block:: python

    def step_1(simulations_data):
        pass

    def step_2(simulations_data):
        pass

    def step_3(simulations_data):
        pass

    def main():
        scenario = [step_1, step_2, step_3]

        api.do_comparison(path_to_sim, scenario)

        api.do_comparison(path_to_sim, step_1)





