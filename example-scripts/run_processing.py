import pathlib as _pl

import pytrnsys_process.process_sim.process_sim as ps
from pytrnsys_process import plotters as plt, utils, headers


def process_single_simulation(
        sim_folder: _pl.Path = _pl.Path("C:/Development/data/results/complete-0-SnkScale0.6000-StoreScale10")):
    simulation = ps.process_sim_prt(sim_folder)

    # Do Calculations

    # Plot
    hourly_line_plot = plt.LinePlot().plot(simulation.hourly, ["QSrc1TIn", "QSrc1TOut"])
    monthly_bar_plot = plt.BarChart().plot(simulation.monthly, [
        "QSnk60P",
        "QSnk60PauxCondSwitch_kW",
    ])

    hourly_line_plot.savefig(_pl.Path(f"C:/Development/data/plots/hourly-plot-{sim_folder.name}.png"))
    monthly_bar_plot.savefig(_pl.Path(f"C:/Development/data/plots/monthly-plot-{sim_folder.name}.png"))


def process_all_simulations():
    results = _pl.Path("C:/Development/data/results")
    sim_folders = utils.get_sim_folders(results)

    for sim_folder in sim_folders:
        process_single_simulation(sim_folder)


def validate_headers():
    death = headers.Headers(_pl.Path("C:/Development/data/results"))
    death.init_headers()
    death.search_header("QSnk60P")


# validate_headers()
process_single_simulation()
