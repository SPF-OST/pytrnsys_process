import pathlib as _pl
import timeit as _ti

import pytrnsys_process.input.trnsys.hourly as hourly

DATA_DIR_PATH = _pl.Path(__file__).parent / "data" / "hourly"


def testControlHourly():
    def runReader():
        controlHourlyFilePath = DATA_DIR_PATH / "control_hr.prt"
        hourly.readHourly(controlHourlyFilePath)
    time_taken = _ti.timeit(runReader, number=100)
    print(f"Time taken to read the CSV: {time_taken:.6f} seconds")
    assert False

def testEbHourly():
        def runReader():
            ebHourlyFilePath = DATA_DIR_PATH / "ENERGY_BALANCE_HR.prt"
            hourly.readHourly(ebHourlyFilePath)
        time_taken = _ti.timeit(runReader, number=100)
        print(f"Time taken to read the CSV: {time_taken:.6f} seconds")
        assert False

