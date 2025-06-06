"""
Comparison plot
==========================

This example demonstrates how to load simulations_data from a pickle and calculate values on the fly.
The newly calculated values are then used to create a comparison plot.
"""

import pathlib as _pl
import matplotlib.pyplot as _plt

from pytrnsys_process import api


def main():
    ###############################################
    # Step 1: Load Data
    # -----------------
    # Load pre-processed simulation data from pickle
    ###############################################

    simulations_data = api.load_simulations_data_from_pickle(
        _pl.Path("../example_data/ice/simulations_data.pickle")
    )

    for sim_name, sim in simulations_data.simulations.items():
        ################################################
        # Step 2: Extract Ice Storage Performance Metrics
        # --------------------------------------------
        # Calculate maximum ice ratio from hourly data
        ################################################

        hourly_data = sim.hourly
        max_ice_ratio = hourly_data["VIceRatio"].max()
        simulations_data.scalar.loc[sim_name, "VIceRatioMax"] = max_ice_ratio

        ##############################################
        # Step 3: Process Energy Demand Data
        # --------------------------------
        # Sum up demands from multiple heat sinks and
        # convert to yearly totals in GWh
        ##############################################

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

        # Unit conversion factor: kWh to GWh
        kwh_to_gwh = 1e-6

        # Process monthly data
        monthly_df = sim.monthly
        monthly_df["total_demand_GWh"] = (
            monthly_df[demand_columns].sum(axis=1) * kwh_to_gwh
        )

        # Calculate yearly total (excluding first 2 months)
        yearly_total = int(monthly_df["total_demand_GWh"].iloc[2::].sum())
        simulations_data.scalar.loc[sim_name, "yearly_demand_GWh"] = (
            yearly_total
        )

    ################################################
    # Step 4: Create Comparison Plot
    # ---------------------------------------
    # scalar compare plot showing:
    # - X-axis: Scaled ice volume (VIceSscaled)
    # - Y-axis: Maximum ice ratio (VIceRatioMax)
    # - Color: Yearly demand in GWh
    # - Markers: DHW to space heating ratio
    ################################################

    api.scalar_compare_plot(
        simulations_data.scalar,
        "VIceSscaled",
        "VIceRatioMax",
        group_by_color="yearly_demand_GWh",
        group_by_marker="ratioDHWtoSH_allSinks",
    )
    _plt.show()


if __name__ == "__main__":
    main()
