import pathlib as _pl

import matplotlib.pyplot as _plt

from pytrnsys_process import api


# Your processing steps are writen inside functions.
# Which need to be defined before your scripts entry point.
# Define your processing steps at the top of the script.
def processing_of_monthly_data(simulation: api.Simulation):
    # create a bar chart using monthly data
    monthly_df = simulation.monthly
    columns_to_plot = ["QSnk60P", "QSnk60PauxCondSwitch_kW"]
    fig, ax = api.bar_chart(
        monthly_df,
        columns_to_plot,
    )

    # modify label for the y axis
    ax.set_ylabel("Power [kW]")

    # This is also done by api.save_plot, but if you want to see your plot before saving it.
    # For example with _plt.show(). Calling this function is required, to make the plot look as expected.
    _plt.tight_layout()

    # create plots folder inside simulation directory and save plot in configured formats
    api.export_plots_in_configured_formats(
        fig, simulation.path, "monthly-bar-chart"
    )


def processing_of_hourly_data(simulation: api.Simulation):
    # create line plot using hourly data
    fig, ax = api.line_plot(simulation.hourly, ["QSrc1TIn", "QSrc1TOut"])

    # Here you can modify anything to do with your plot, according to the matplotlib.pyplot standard
    ax.set_ylabel("Temperature [°C]")
    # make label fit inside your plot
    _plt.tight_layout()

    # create plots folder inside simulation directory and save plot in configured formats
    api.export_plots_in_configured_formats(
        fig, simulation.path, "hourly-line-plot"
    )


def processing_for_histogram(simulation: api.Simulation):
    # create histogram using hourly data
    fig, _ = api.histogram(simulation.hourly, ["QSrc1TIn"])

    # if you don't want to export your plot, you can also just show it by calling this function
    _plt.show()


if __name__ == "__main__":
    # This is the entry point to your script.
    # Here, you can decide how you would like to run your processing steps.
    # In the example below we run both processing steps on a whole result set.
    # Or a single processing step on a single simulation.
    # Make sure to remove the lines you do not want to run.

    # bundle the steps into a list
    processing_scenarios = [
        processing_of_monthly_data,
        processing_of_hourly_data,
    ]

    # run the scenarios on a whole result set
    (
        api.process_whole_result_set(
            _pl.Path("data/results"),
            processing_scenarios,
        )
    )

    # run the single scenario on a single simulation
    (
        api.process_single_simulation(
            _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
            # ===============================================================
            processing_for_histogram,
            # do not add round brackets when linking your processing step
            # processing_for_histogram AND NOT processing_for_histogram()
            # ===============================================================
        )
    )
