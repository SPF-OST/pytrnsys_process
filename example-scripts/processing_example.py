import pathlib as _pl

import pytrnsys_process as pp


def processing_scenario(simulation):
    # create line plot using hourly data
    hourly_line_plot = pp.line_plot(
        simulation.hourly, ["QSrc1TIn", "QSrc1TOut"]
    )
    # create bar chart using monthly data
    monthly_bar_chart = pp.bar_chart(
        simulation.monthly,
        [
            "QSnk60P",
            "QSnk60PauxCondSwitch_kW",
        ],
    )
    # create stacked bar chart using monthly data
    monthly_stacked_bar_chart = pp.stacked_bar_chart(
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

    # create plots folder in simulation directory
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


# run processing scenario for a whole result set
if __name__ == "__main__":
    pp.process_whole_result_set(
        _pl.Path("path/to/result/set"),
        processing_scenario,
    )
