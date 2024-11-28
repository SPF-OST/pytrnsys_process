import pathlib as _pl

import pytrnsys_process.process_batch as pb
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "results")
INVALID_RESULTS_FOLDER = _pl.Path(const.DATA_FOLDER / "invalid-results")


def processing_scenario(simulation):
    assert not simulation.monthly.empty


class TestPytrnsysProcess:

    def test_process_single_simulation(self):
        sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")
        results = pb.process_single_simulation(sim_folder, processing_scenario)
        assert results.processed_count == 1
        assert results.error_count == 0
        assert results.failed_simulations == []

    def test_process_whole_result_set(self):
        results = pb.process_whole_result_set(
            RESULTS_FOLDER, processing_scenario
        )
        assert results.processed_count == 2
        assert results.error_count == 0
        assert results.failed_simulations == []

    def test_process_whole_result_set_parallel(self):
        results = pb.process_whole_result_set_parallel(
            RESULTS_FOLDER, processing_scenario
        )
        assert results.processed_count == 2
        assert results.error_count == 0
        assert results.failed_simulations == []

    def test_process_single_simulation_with_invalid_data(self):
        sim_folder = _pl.Path(INVALID_RESULTS_FOLDER / "sim-1")
        results = pb.process_single_simulation(sim_folder, processing_scenario)
        assert results.processed_count == 0
        assert results.error_count == 1
        assert results.failed_simulations == ["sim-1"]

    def test_process_whole_result_set_with_invalid_data(self):
        results = pb.process_whole_result_set(
            INVALID_RESULTS_FOLDER, processing_scenario
        )
        assert results.processed_count == 0
        assert results.error_count == 2
        assert results.failed_simulations == ["sim-1", "sim-2"]

    def test_process_whole_result_set_parallel_with_invalid_data(self):
        results = pb.process_whole_result_set_parallel(
            INVALID_RESULTS_FOLDER, processing_scenario
        )
        assert results.processed_count == 0
        assert results.error_count == 2
        assert all(sim in results.failed_simulations for sim in ["sim-1", "sim-2"])


class TestBenchmarkPytrnsysProcess:
    def test_benchmark_process_whole_result_set(self, benchmark):
        benchmark(
            pb.process_whole_result_set, RESULTS_FOLDER, processing_scenario
        )

    def test_benchmark_process_whole_result_set_parallel(self, benchmark):
        benchmark(
            pb.process_whole_result_set_parallel,
            RESULTS_FOLDER,
            processing_scenario,
        )
