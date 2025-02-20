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
    # _plt.tight_layout()

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
    # _plt.tight_layout()

    # create plots folder inside simulation directory and save plot in configured formats
    api.export_plots_in_configured_formats(
        fig, simulation.path, "hourly-line-plot"
    )


def processing_for_histogram(simulation: api.Simulation):
    # create histogram using hourly data
    api.histogram(simulation.hourly, ["QSrc1TIn"])

    # if you don't want to export your plot, you can also just show it by calling this function
    _plt.show()


def calc_total_yearly_demand_per_sim(
        simulations_data: api.SimulationsData,
) -> api.SimulationsData:
    # Columns to sum
    demand_columns = [
        "qSysOut_QSnk131Demand",
        "qSysOut_QSnk183Demand",
        "qSysOut_QSnk191Demand",
        "qSysOut_QSnk225Demand",
        "qSysOut_QSnk243Demand",
        "qSysOut_QSnk266Demand",
        "qSysOut_QSnk322Demand",
        "qSysOut_QSnk335Demand",
        "qSysOut_QSnk358Demand",
        "qSysOut_QSnk417Demand",
        "qSysOut_QSnk448Demand",
        "qSysOut_QSnk469Demand",
        "qSysOut_QSnk488Demand",
        "qSysOut_QSnk524Demand",
        "qSysOut_QSnk539Demand",
        "qSysOut_QSnk558Demand",
        "qSysOut_QSnk579Demand",
        "qSysOut_QSnk60Demand",
        "qSysOut_QSnk85Demand",
    ]
    # Conversion to gwh
    kwh_to_gwh = 1e-6
    # Iterate through each simulation
    for sim_name, sim in simulations_data.simulations.items():
        # Access the monthly data
        monthly_df = sim.monthly
        # Calculate total monthly demand in GWh (sum columns and convert from kWh)
        monthly_df["total_demand_GWh"] = (
                monthly_df[demand_columns].sum(axis=1) * kwh_to_gwh
        )

        # Sum Jan-December values (skip first 2 months - typically Nov/Dec)
        # Wrap in int to get rid of decimal places
        yearly_total = int(monthly_df["total_demand_GWh"].iloc[2::].sum())

        # Store result in scalar data for comparison
        simulations_data.scalar.loc[sim_name, "yearly_demand_GWh"] = (
            yearly_total
        )
    return simulations_data


def calc_v_ice_ratio_max_per_sim(
        simulations_data: api.SimulationsData,
) -> api.SimulationsData:
    # Iterate through each simulation's hourly data
    for sim_name, sim in simulations_data.simulations.items():
        # Access hourly data
        hourly_data = sim.hourly
        # Get maximum VIceRatio value from hourly timeseries
        max_ice_ratio = hourly_data["VIceRatio"].max()
        # Store result in scalar data table using simulation name as index
        simulations_data.scalar.loc[sim_name, "VIceRatioMax"] = max_ice_ratio
    return simulations_data


def comparison_of_scalar_data(
        simulations_data: api.SimulationsData,
):
    # Calculate and add two new metrics to the results:
    # 1. Total yearly energy demand in GWh
    # 2. Maximum ice storage ratio from hourly data

    # Grouping steps will ensure that the failure of a dependent step will cause the whole process to fail.
    simulations_data = calc_total_yearly_demand_per_sim(simulations_data)
    simulations_data = calc_v_ice_ratio_max_per_sim(simulations_data)

    # Create a scatter plot for comparison comparing:
    fig, _ = api.scatter_plot(
        simulations_data.scalar,
        "VIceSscaled",
        "VIceRatioMax",
        group_by_color="yearly_demand_GWh",
        group_by_marker="ratioDHWtoSH_allSinks",
    )

    # save plots in the results folder in the configured formats
    api.export_plots_in_configured_formats(
        fig,
        simulations_data.path_to_simulations,
        "compare-plot",
        plots_folder_name="",
    )


def main():
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

    # run the scenarios on a whole result using multiple processes
    simulations_data = api.process_whole_result_set_parallel(
        _pl.Path(api.REPO_ROOT / "examples/ready_to_run/data/results"),
        processing_scenarios,
    )

    # using the data from processing multiple simulations, run your comparisons steps
    api.do_comparison(simulations_data, comparison_of_scalar_data)

    # run the single scenario on a single simulation
    (
        api.process_single_simulation(
            _pl.Path(
                api.REPO_ROOT
                / "examples/ready_to_run/data/results/complete-0-SnkScale0.8000-StoreScale10"
            ),
            # ===============================================================
            processing_for_histogram,
            # do not add round brackets when linking your processing step
            # processing_for_histogram AND NOT processing_for_histogram()
            # ===============================================================
        )
    )


# This is required since we would like to run the script directly
if __name__ == "__main__":
    main()
