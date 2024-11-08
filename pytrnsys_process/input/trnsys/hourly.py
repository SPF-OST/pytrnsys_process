import datetime as _dt
import pathlib as _pl

import pandas as _pd
# def readHourlyFile(prtFilePath: _pl.Path)  -> _pd.DataFrame:
#     df = _pd.read_csv(prtFilePath, header=1, delimiter=r"\s+")

def readHourly(prtFilePath: _pl.Path, skipfooter=24, header=1, delimiter=r"\s+")  -> _pd.DataFrame:
    df = _pd.read_csv(prtFilePath, skipfooter=skipfooter, header=header, delimiter=delimiter)
    return df











