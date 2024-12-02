import pathlib as _pl

import matplotlib.pyplot as _plt

import pytrnsys_process as pp


# Your processing steps are writen inside functions.
# Which need to be defined before your scripts entry point.
# Define your processing steps at the top of the script.
def processing_of_monthly_data(simulation: pp.Simulation):
    # create a bar chart using monthly data
    monthly_df = simulation.monthly
    columns_to_plot = ["QSnk60P", "QSnk60PauxCondSwitch_kW"]
    fig, ax = pp.bar_chart(
        monthly_df,
        columns_to_plot,
    )

    # modify label for the y axis
    ax.set_ylabel("Power [kW]")
    # make label fit inside your plot
    _plt.tight_layout()

    # create plots folder inside simulation directory and save plot
    plots_folder = _pl.Path(simulation.path / "plots")
    plots_folder.mkdir(exist_ok=True)
    fig.savefig(_pl.Path(f"{plots_folder}/monthly-bar-chart.png"))


def processing_of_hourly_data(simulation: pp.Simulation):
    # create line plot using hourly data
    fig, ax = pp.line_plot(simulation.hourly, ["QSrc1TIn", "QSrc1TOut"])

    # modify label for the y axis
    ax.set_ylabel("Temperature [°C]")
    # make label fit inside your plot
    _plt.tight_layout()

    # create plots folder inside simulation directory and save plot
    plots_folder = _pl.Path(simulation.path / "plots")
    plots_folder.mkdir(exist_ok=True)
    fig.savefig(_pl.Path(f"{plots_folder}/hourly-line-plot.png"))


def processing_for_histogram(simulation: pp.Simulation):
    # create histogram using hourly data
    fig, _ = pp.histogram(simulation.hourly, ["QSrc1TIn"])

    # create plots folder inside simulation directory and save plot
    plots_folder = _pl.Path(simulation.path / "plots")
    plots_folder.mkdir(exist_ok=True)
    fig.savefig(_pl.Path(f"{plots_folder}/histogram.png"))


if __name__ == "__main__":
    # This is the entry point to your script.
    # In here you can decide how you would like to run your processing steps.
    # In the example below we run both processing steps on a whole result set.
    # Or a single processing step on a single simulation.
    # Make sure to remove the lines you do not want to run. 

    # bundle the scenarios into a list
    processing_scenarios = [
        processing_of_monthly_data,
        processing_of_hourly_data,
    ]

    # run the scenarios on a whole result set
    pp.process_whole_result_set(
        _pl.Path("data/results"),
        processing_scenarios,
    )

    # run the single scenario on a single simulation
    pp.process_single_simulation(
        _pl.Path("data/results/complete-0-SnkScale0.6000-StoreScale8"),
        # ===============================================================
        processing_for_histogram,
        # do not add round brackets when linking your processing step
        # processing_for_histogram AND NOT processing_for_histogram()
        # ===============================================================
    )
