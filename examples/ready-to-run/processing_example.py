import pathlib as _pl

import matplotlib.pyplot as _plt

import pytrnsys_process as pp


def processing_of_monthly_data(simulation: pp.Simulation):
    # crate a bar chart using monthly data
    fig, ax = pp.bar_chart(
        simulation.monthly,
        [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ],
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
        processing_for_histogram,
    )
