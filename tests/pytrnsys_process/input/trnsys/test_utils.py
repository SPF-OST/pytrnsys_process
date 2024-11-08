import pathlib as _pl
import timeit as _ti
import pytrnsys_process.input.trnsys.utils as utils

PATH_TO_RESULTS = _pl.Path("C:/Development/data/results")

NUMBER_OF_RUNS = 1


# TODO create test data with min amount of files
# TODO test multi threading with reading hourly energy balance
class TestUtils:

    def testFindAllVariables(self):
        def findAllVariables():
            utils.findAllVariables(PATH_TO_RESULTS)

        averageTimeTaken = (
            _ti.timeit(findAllVariables, number=NUMBER_OF_RUNS)
            / NUMBER_OF_RUNS
        )
        print(
            f"Average time taken to find all variables single thread: {averageTimeTaken:.6f} seconds"
        )

    def testFindAllVariablesMultiThread(self):
        def findAllVariables():
            utils.findAllVariablesMultiThread()

        averageTimeTaken = (
            _ti.timeit(findAllVariables, number=NUMBER_OF_RUNS)
            / NUMBER_OF_RUNS
        )
        print(
            f"Average time taken to find all variables multi thread: {averageTimeTaken:.6f} seconds"
        )
