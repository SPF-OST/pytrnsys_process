import pathlib as _pl
from unittest import mock as _mock

import pytest as _pt

import pytrnsys_process.process_batch as pb
from pytrnsys_process import data_structures as ds
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")
INVALID_RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "invalid-results")


@_pt.fixture(autouse=True)
def mock_save_to_pickle(monkeypatch):
    mock = _mock.Mock()
    monkeypatch.setattr("pytrnsys_process.utils.save_to_pickle", mock)


def processing_step(simulation: ds.Simulation):
    assert not simulation.monthly.empty


def processing_step_failing(simulation: ds.Simulation):
    assert not simulation.monthly.empty
    raise ValueError("Intentional failure for testing")


def comparison_step(simulations_data: ds.SimulationsData):
    assert len(simulations_data.simulations) == 2
    assert all(
        not sim.monthly.empty for sim in simulations_data.simulations.values()
    )
    assert all(
        not sim.hourly.empty for sim in simulations_data.simulations.values()
    )
    assert simulations_data.scalar.shape == (2, 10)


class TestPytrnsysProcess:

    def test_process_single_simulation(self):
        sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
        results = pb.process_single_simulation(
            sim_folder, [processing_step, processing_step_failing]
        )
        assert results.monthly.shape == (14, 11)
        assert results.hourly.shape == (3, 18)
        assert results.scalar.shape == (1, 10)
        assert results.step.shape == (0, 0)

    def test_process_whole_result_set(self):
        results = pb.process_whole_result_set(
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
        results = pb.process_whole_result_set_parallel(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        assert results.simulations["sim-1"].hourly.shape == (3, 18)
        assert results.simulations["sim-1"].monthly.shape == (14, 11)
        assert results.simulations["sim-1"].step.shape == (0, 0)
        assert results.simulations["sim-2"].hourly.shape == (0, 0)
        assert results.simulations["sim-2"].monthly.shape == (14, 11)
        assert results.simulations["sim-2"].step.shape == (0, 0)
        assert results.scalar.shape == (2, 10)

    def test_process_single_simulation_with_invalid_data(self):
        sim_folder = _pl.Path(INVALID_RESULTS_FOLDER / "sim-1")

        with _pt.raises(pb.UnableToProcessSimulationError) as exc_info:
            pb.process_single_simulation(sim_folder, processing_step)

        assert (
                str(exc_info.value)
                == f"Failed to process simulation in {sim_folder}"
        )

    def test_process_whole_result_set_with_invalid_data(self):
        results = pb.process_whole_result_set(
            INVALID_RESULTS_FOLDER, processing_step
        )
        assert len(results.simulations) == 0
        assert results.scalar.empty

    def test_process_whole_result_set_parallel_with_invalid_data(self):
        results = pb.process_whole_result_set_parallel(
            INVALID_RESULTS_FOLDER, processing_step
        )
        assert len(results.simulations) == 0
        assert results.scalar.empty

    def test_do_comparison(self):
        results = pb.process_whole_result_set(RESULTS_FOLDER, processing_step)
        pb.do_comparison(results, comparison_step)


class TestBenchmarkPytrnsysProcess:
    def test_benchmark_process_whole_result_set(self, benchmark):
        benchmark(pb.process_whole_result_set, RESULTS_FOLDER, processing_step)

    def test_benchmark_process_whole_result_set_parallel(self, benchmark):
        benchmark(
            pb.process_whole_result_set_parallel,
            RESULTS_FOLDER,
            processing_step,
        )
