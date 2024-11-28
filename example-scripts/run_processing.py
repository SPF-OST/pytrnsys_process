import pathlib as _pl

import pytrnsys_process.process_batch as pb
import pytrnsys_process.process_sim.process_sim as ps
from pytrnsys_process import plotters as plt


def processing_scenario(simulation: ps.Simulation):
    # create line plot using hourly data
    hourly_line_plot = plt.LinePlot().plot(
        simulation.hourly, ["QSrc1TIn", "QSrc1TOut"]
    )
    # create bar chart using monthly data
    monthly_bar_chart = plt.BarChart().plot(
        simulation.monthly,
        [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ],
    )
    # create stacked bar chart using monthly data
    monthly_stacked_bar_chart = plt.StackedBarChart().plot(
        simulation.monthly,
        [
            "QSnk60PauxCondSwitch_kW",
            "QSnk60dQ",
            "QSnk60P",
            "QSnk60PDhw",
            "QSnk60dQlossTess",
            "QSnk60qImbTess",
        ],
    )

    plots_folder = _pl.Path(simulation.path / "plots")
    plots_folder.mkdir(exist_ok=True)

    # Save your plots
    hourly_line_plot.savefig(_pl.Path(f"{plots_folder}/hourly-line-plot.png"))
    monthly_bar_chart.savefig(
        _pl.Path(f"{plots_folder}/monthly-bar-chart.png")
    )
    monthly_stacked_bar_chart.savefig(
        _pl.Path(f"{plots_folder}/monthly-stacked-bar-chart.png")
    )


if __name__ == "__main__":
    pb.process_whole_result_set(
        _pl.Path("C:/Development/data/results"),
        processing_scenario,
    )

# pp.process_single_simulation(
#     _pl.Path(
#         "C:/Development/data/results/complete-0-SnkScale0.6000-StoreScale10"
#     ),
#     processing_scenario,
# )

# if __name__ == "__main__":
#     pp.process_whole_result_set_parallel(
#         _pl.Path("C:/Development/data/results"),
#         processing_scenario,
#     )
