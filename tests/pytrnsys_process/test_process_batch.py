import pathlib as _pl
from unittest import mock as _mock

import pytest as _pt

from pytrnsys_process import process

# from pytrnsys_process.process import process_batch as pb
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")
INVALID_RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "invalid-results")


@_pt.fixture(autouse=True)
def mock_save_to_pickle(monkeypatch):
    mock = _mock.Mock()
    monkeypatch.setattr("pytrnsys_process.util.save_to_pickle", mock)


def processing_step(simulation: process.Simulation):
    assert not simulation.monthly.empty


def processing_step_failing(simulation: process.Simulation):
    assert not simulation.monthly.empty
    raise ValueError("Intentional failure for testing")


def comparison_step(simulations_data: process.SimulationsData): # pylint: disable=unused-argument
    return


def assert_comparison(simulations_data: process.SimulationsData):
    assert len(simulations_data.simulations) == 2

    assert all(
        not sim.monthly.empty for sim in simulations_data.simulations.values()
    )

    assert not simulations_data.simulations["sim-1"].hourly.empty
    assert simulations_data.simulations["sim-2"].hourly.empty

    assert simulations_data.scalar.shape == (2, 10)


class TestPytrnsysProcess:

    def test_process_single_simulation(self):
        sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
        results = process.process_single_simulation(
            sim_folder, [processing_step, processing_step_failing]
        )
        assert results.monthly.shape == (14, 11)
        assert results.hourly.shape == (3, 18)
        assert results.scalar.shape == (1, 10)
        assert results.step.shape == (0, 0)

    def test_process_whole_result_set(self):
        results = process.process_whole_result_set(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        assert results.simulations["sim-1"].hourly.shape == (3, 18)
        assert results.simulations["sim-1"].monthly.shape == (14, 11)
        assert results.simulations["sim-1"].step.shape == (0, 0)
        assert results.simulations["sim-2"].hourly.shape == (0, 0)
        assert results.simulations["sim-2"].monthly.shape == (14, 11)
        assert results.simulations["sim-2"].step.shape == (0, 0)
        assert results.scalar.shape == (2, 10)

    def test_process_whole_result_set_parallel(self):
        results = process.process_whole_result_set_parallel(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        assert results.simulations["sim-1"].hourly.shape == (3, 18)
        assert results.simulations["sim-1"].monthly.shape == (14, 11)
        assert results.simulations["sim-1"].step.shape == (0, 0)
        assert results.simulations["sim-2"].hourly.shape == (0, 0)
        assert results.simulations["sim-2"].monthly.shape == (14, 11)
        assert results.simulations["sim-2"].step.shape == (0, 0)
        assert results.scalar.shape == (2, 10)

    # def test_process_single_simulation_with_invalid_data(self):
    #     sim_folder = _pl.Path(INVALID_RESULTS_FOLDER / "sim-1")
    #
    #     with _pt.raises(pb.UnableToProcessSimulationError) as exc_info:
    #         process.process_single_simulation(sim_folder, processing_step)
    #
    #     assert (
    #         str(exc_info.value)
    #         == f"Failed to process simulation in {sim_folder}"
    #     )
    #
    # def test_process_whole_result_set_with_invalid_data(self):
    #     results = process.process_whole_result_set(
    #         INVALID_RESULTS_FOLDER, processing_step
    #     )
    #     assert len(results.simulations) == 0
    #     assert results.scalar.empty
    #
    # def test_process_whole_result_set_parallel_with_invalid_data(self):
    #     results = process.process_whole_result_set_parallel(
    #         INVALID_RESULTS_FOLDER, processing_step
    #     )
    #     assert len(results.simulations) == 0
    #     assert results.scalar.empty

    def test_do_comparison_with_existing_results_for_comparison(self):
        results = process.process_whole_result_set(
            RESULTS_FOLDER, processing_step
        )
        simulations_data = process.do_comparison(
            comparison_step, simulations_data=results
        )
        assert_comparison(simulations_data)

    def test_do_comparison_by_passing_path_to_results_folder(
        self
    ):
        simulations_data = process.do_comparison(
            comparison_step, results_folder=RESULTS_FOLDER
        )
        assert_comparison(simulations_data)

    def test_do_comparison_with_existing_pickle(self):
        simulations_data = process.do_comparison(
            comparison_step, results_folder=const.DATA_FOLDER / "pickle"
        )
        assert_comparison(simulations_data)

    def test_do_comparison_with_missing_args(self):
        with _pt.raises(ValueError) as exc_info:
            process.do_comparison(comparison_step)

        assert (
            str(exc_info.value)
            == "Either simulations_data or results_folder must be provided to perform comparison"
        )


class TestBenchmarkPytrnsysProcess:
    def test_benchmark_process_whole_result_set(self, benchmark):
        benchmark(
            process.process_whole_result_set, RESULTS_FOLDER, processing_step
        )

    def test_benchmark_process_whole_result_set_parallel(self, benchmark):
        benchmark(
            process.process_whole_result_set_parallel,
            RESULTS_FOLDER,
            processing_step,
        )
