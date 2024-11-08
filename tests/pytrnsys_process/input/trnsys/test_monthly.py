# pylint: disable=missing-module-docstring

import pathlib as _pl

import pytrnsys_process.input.trnsys.monthly as _monthly

DATA_DIR_PATH = _pl.Path(__file__).parent / "data" / "monthly"


def test():
    monthly_file_path = DATA_DIR_PATH / "BUILDING_MO.Prt"
    actual_df = _monthly.read_monthly_file(monthly_file_path, starting_year=1990)

    actual_file_path = DATA_DIR_PATH / "actual.csv"
    actual_df.to_csv(actual_file_path, encoding="UTF8")

    expected_file_path = DATA_DIR_PATH / "expected.csv"

    assert actual_file_path.read_text(encoding="UTF8") == expected_file_path.read_text(encoding="UTF8")

def testEnergyBalanceMonthly():
    ebMonthlyFilePath = DATA_DIR_PATH / "ENERGY_BALANCE_MO.Prt"
    df = _monthly.read_monthly_file(ebMonthlyFilePath, starting_year=1990, starting_month=11)
    csv_file_path = DATA_DIR_PATH / "energy_balance_mo.csv"

    df.to_csv(csv_file_path, encoding="UTF-8")

    assert False

def testGetAllAvailableVariables():
    ebMonthlyFilePath = DATA_DIR_PATH / "ENERGY_BALANCE_MO.Prt"
    _monthly.getAllAvailableVariables(ebMonthlyFilePath)
    assert False


# def test_api_idea():
#     fig, axs = plot_monthly_balance(energyIn=["PelPVRoof_kW"], energyOut=["PvToBat_kW", "PvToHeatSys_kW","PvToHH_kW", "PvToGrid_kW"], **kwargs)
#     fig, axs = plot_monthly_balance(data, energyIn=["PelPVRoof_kW"], energyOut=["PvToBat_kW", "PvToHeatSys_kW","PvToHH_kW", "PvToGrid_kW"], **kwargs)
#     "PelPVRoof_kW" "-PvToBat_kW" "-PvToHeatSys_kW" "-PvToHH_kW" "-PvToGrid_kW"
#
#     add_variables_into_new_variable(new_variable='var_new', vars_to_add=['var1', 'var2'])

