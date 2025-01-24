import pathlib as _pl

import pytrnsys_process.process_batch as pb
from pytrnsys_process.process_sim import process_sim as ps
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")
INVALID_RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "invalid-results")


def processing_step(simulation: ps.Simulation):
    assert not simulation.monthly.empty


def processing_step_failing(simulation: ps.Simulation):
    assert not simulation.monthly.empty
    raise ValueError("Intentional failure for testing")


def comparison_step(results_for_comparison: pb.ResultsForComparison):
    assert len(results_for_comparison.hourly) == 2
    assert len(results_for_comparison.monthly) == 2
    assert results_for_comparison.scalar.shape == (2, 10)


class TestPytrnsysProcess:

    def test_process_single_simulation(self):
        sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
        results = pb.process_single_simulation(
            sim_folder, [processing_step, processing_step_failing]
        )
        assert len(results.monthly) == 1
        assert len(results.hourly) == 1
        assert results.scalar.shape[0] == 1
        assert "sim-1" in results.monthly
        assert "sim-1" in results.hourly

    def test_process_whole_result_set(self):
        results = pb.process_whole_result_set(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        assert len(results.monthly) == 2
        assert len(results.hourly) == 2
        assert results.scalar.shape[0] == 2
        assert all(sim in results.monthly for sim in ["sim-1", "sim-2"])
        assert all(sim in results.hourly for sim in ["sim-1", "sim-2"])

    def test_process_whole_result_set_parallel(self):
        results = pb.process_whole_result_set_parallel(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        assert len(results.monthly) == 2
        assert len(results.hourly) == 2
        assert results.scalar.shape[0] == 2
        assert all(sim in results.monthly for sim in ["sim-1", "sim-2"])
        assert all(sim in results.hourly for sim in ["sim-1", "sim-2"])

    def test_process_single_simulation_with_invalid_data(self):
        sim_folder = _pl.Path(INVALID_RESULTS_FOLDER / "sim-1")
        results = pb.process_single_simulation(sim_folder, processing_step)
        assert len(results.monthly) == 0
        assert len(results.hourly) == 0
        assert results.scalar.empty

    def test_process_whole_result_set_with_invalid_data(self):
        results = pb.process_whole_result_set(
            INVALID_RESULTS_FOLDER, processing_step
        )
        assert len(results.monthly) == 0
        assert len(results.hourly) == 0
        assert results.scalar.empty

    def test_process_whole_result_set_parallel_with_invalid_data(self):
        results = pb.process_whole_result_set_parallel(
            INVALID_RESULTS_FOLDER, processing_step
        )
        assert len(results.monthly) == 0
        assert len(results.hourly) == 0
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
