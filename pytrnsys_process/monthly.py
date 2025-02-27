"""Functionality to read monthly data from a TRNSYS simulation"""

import datetime as _dt
import pathlib as _pl

import pandas as _pd

_N_ROWS_USED = 12


def read_monthly_file(
    prt_file_path: _pl.Path, starting_year: int = 2001
) -> _pd.DataFrame:
    """Load monthly data written by Type 46 as a `pandas` `DataFrame`.

    Parameters
    __________
    prt_file_path:
        Path to printer file

    starting_year:
        Year onto which hours contained in the printer file will be added to arrive
        at a full time stamp (e.g. `starting_year == 1984` plus 3624.0 hours => 00:00:00 June 1, 1984)


    Returns
    _______
    DataFrame:
        A data frame containing the data in the prt file which has as an index the time stamps
        of the data


    Examples
    ________
        >>> import pytrnsys_process.monthly as _monthly
        >>> import tests.pytrnsys_process.test_monthly as _test
        >>> prt_file_path = _test.DATA_DIR_PATH / "BUILDING_MO.Prt"
        >>> _monthly.read_monthly_file(prt_file_path, starting_year=1990)
                     PBuiSol_kW  PBuiGains_KW  ...  PbuiVent_kW  PAcumBui_kW
        Timestamp                              ...
        1990-02-01   780.877209   1855.802086  ... -2449.556250  -185.337733
        1990-03-01  1020.135986   1681.815691  ... -2194.195954   -40.804481
        1990-04-01  1624.960201   1860.622298  ... -2470.592889   -74.430886
        1990-05-01  1952.101631   1801.632508  ... -2516.026618   180.830862
        1990-06-01  2483.275600   1846.998399  ... -1788.616619   146.297929
        1990-07-01  2753.366807   1797.206624  ... -1260.036783  -382.267725
        1990-08-01  2585.046461   1855.984069  ...  -941.706180   268.287364
        1990-09-01  2636.095017   1846.078276  ...  -738.181275  -484.410362
        1990-10-01  1874.110338   1811.402719  ... -1797.426500   229.671108
        1990-11-01  1289.769752   1853.183395  ... -2354.109776   161.956260
        1990-12-01   801.932105   1797.973707  ... -2552.764194   128.235225
        1991-01-01   672.317375   1875.200216  ... -2387.085933   -62.726139
        <BLANKLINE>
        [12 rows x 8 columns]

    Note
    _____
    Notice how the time stamps are given **at the end of a month**.

    """
    df = _pd.read_csv(
        prt_file_path, header=1, delimiter=r"\s+", nrows=_N_ROWS_USED
    )
    df = df.rename(columns=lambda x: x.strip())

    hours = _dt.timedelta(hours=1) * df["Time"]  # type: ignore
    start_of_year = _dt.datetime(day=1, month=1, year=starting_year)
    actual_ends_of_month = start_of_year + hours

    expected_ends_of_months = _pd.date_range(
        start_of_year, periods=12, freq="ME"
    ) + _dt.timedelta(days=1)

    if (actual_ends_of_month != expected_ends_of_months).any():
        raise ValueError(
            f"The time stamps of the supposedly monthly file '{prt_file_path}' don't fall on the end of each month."
        )

    df = df.drop(columns=["Month", "Time"])

    df["Timestamp"] = actual_ends_of_month
    df = df.set_index("Timestamp")

    return df
