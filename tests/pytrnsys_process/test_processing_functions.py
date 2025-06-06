import logging as _logging
import pathlib as _pl
from unittest import mock as _mock

import matplotlib.pyplot as _plt
import pytest as _pt

from pytrnsys_process import process, config
# from pytrnsys_process.process import process_batch as pb
from tests.pytrnsys_process import constants as const

RESULTS_FOLDER = const.DATA_FOLDER / "processing-functions/results"
INVALID_RESULTS_FOLDER = (
        const.DATA_FOLDER / "processing-functions/invalid-results"
)
PICKLE_FOLDER = const.DATA_FOLDER / "processing-functions/pickle"


@_pt.fixture(autouse=True)
def setup():
    pickle_files = RESULTS_FOLDER.rglob("*.pickle")
    for file_path in pickle_files:
        file_path.unlink()
    config.global_settings.reader.force_reread_prt = False


def processing_step(
        simulation: process.Simulation,
):  # pylint: disable=unused-argument
    pass


def processing_step_failing(simulation: process.Simulation):
    assert not simulation.monthly.empty
    raise ValueError("Intentional failure for testing")


def comparison_step(
        simulations_data: process.SimulationsData,
):  # pylint: disable=unused-argument
    return


def assert_comparison(simulations_data: process.SimulationsData):
    assert len(simulations_data.simulations) == 2

    assert all(
        not sim.monthly.empty for sim in simulations_data.simulations.values()
    )

    assert not simulations_data.simulations["sim-1"].hourly.empty
    assert simulations_data.simulations["sim-2"].hourly.empty

    assert simulations_data.scalar.shape == (2, 10)


class TestProcessingFunctions:

    @staticmethod
    def assert_for_whole_result_set(simulations_data):
        assert simulations_data.simulations["sim-1"].hourly.shape == (3, 18)
        assert simulations_data.simulations["sim-1"].monthly.shape == (14, 11)
        assert simulations_data.simulations["sim-1"].step.shape == (0, 0)
        assert simulations_data.simulations["sim-2"].hourly.shape == (0, 0)
        assert simulations_data.simulations["sim-2"].monthly.shape == (14, 11)
        assert simulations_data.simulations["sim-2"].step.shape == (0, 0)
        assert simulations_data.scalar.shape == (2, 10)

    def test_process_single_simulation(self, caplog):
        sim_folder = _pl.Path(RESULTS_FOLDER / "sim-1")

        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.INFO):
                return process.process_single_simulation(
                    sim_folder, [processing_step, processing_step_failing]
                )

        # first pass reading from raw files
        run_with_caplog()
        assert "Processing simulation from raw files" in caplog.text

        # second pass reading from pickle
        run_with_caplog()
        assert "Loading simulation from pickle file" in caplog.text

        # third pass with force reread
        config.global_settings.reader.force_reread_prt = True
        sim = run_with_caplog()
        assert "Processing simulation from raw files" in caplog.text

        assert sim.monthly.shape == (14, 11)
        assert sim.hourly.shape == (3, 18)
        assert sim.scalar.shape == (1, 10)
        assert sim.step.shape == (0, 0)
        assert sim.scalar["mfrSolverAbsTol"][0] == -4.999999

    def test_process_whole_result_set(self, caplog):
        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.INFO):
                return process.process_whole_result_set(
                    RESULTS_FOLDER, [processing_step, processing_step_failing]
                )

        # first pass reading from raw files
        run_with_caplog()
        assert caplog.text.count("Processing simulation from raw files") == 2

        # second pass reading from pickle
        run_with_caplog()
        assert caplog.text.count("Loading simulation from pickle file") == 2

        # third pass with force reread
        config.global_settings.reader.force_reread_prt = True
        simulations_data = run_with_caplog()
        assert caplog.text.count("Processing simulation from raw files") == 2

        self.assert_for_whole_result_set(simulations_data)

    def test_process_whole_result_set_parallel(self, monkeypatch):
        # Caplog and monkeypatch don't support multiprocessing in spawn mode :/
        # This is a cheap workaround

        # first pass reading from raw files
        simulations_data = process.process_whole_result_set_parallel(
            RESULTS_FOLDER, [processing_step, processing_step_failing]
        )
        self.assert_for_whole_result_set(simulations_data)

        # mock because we do not want to generate a simulations_data pickle in  the pickle results
        mock = _mock.Mock()
        monkeypatch.setattr("pytrnsys_process.util.save_to_pickle", mock)

        # second pass using pickle only folder, to make sure read from pickle works
        simulations_data = process.process_whole_result_set_parallel(
            PICKLE_FOLDER, [processing_step, processing_step_failing]
        )
        self.assert_for_whole_result_set(simulations_data)

        # Third pass with force reread and pickle only results.
        # should return empty SimulationsData object, since raw files don't exist in this directory.
        config.global_settings.reader.force_reread_prt = True
        simulations_data = process.process_whole_result_set_parallel(
            PICKLE_FOLDER, [processing_step, processing_step_failing]
        )
        assert simulations_data.simulations["sim-1"].hourly.empty
        assert simulations_data.simulations["sim-1"].monthly.empty
        assert simulations_data.simulations["sim-1"].step.empty
        assert simulations_data.simulations["sim-2"].hourly.empty
        assert simulations_data.simulations["sim-2"].monthly.empty
        assert simulations_data.simulations["sim-2"].step.empty
        assert simulations_data.scalar.empty

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

    def test_do_comparison_by_passing_path_to_results_folder(self):
        simulations_data = process.do_comparison(
            comparison_step, results_folder=RESULTS_FOLDER
        )
        assert_comparison(simulations_data)

    def test_do_comparison_with_existing_pickle(self):
        simulations_data = process.do_comparison(
            comparison_step, results_folder=PICKLE_FOLDER
        )
        assert_comparison(simulations_data)

    def test_do_comparison_with_missing_args(self):
        with _pt.raises(ValueError) as exc_info:
            process.do_comparison(comparison_step)

        assert (
                str(exc_info.value)
                == "Either simulations_data or results_folder must be provided to perform comparison"
        )


def processing_step_with_figure(simulation: process.Simulation):
    """Used to check whether figures are closed automatically
    after the processing step finishes."""
    _, _ = _plt.subplots(2, 1)
    _, _ = _plt.subplots(2, 1)


def processing_step_with_figure_shown(simulation: process.Simulation):
    """Used to check whether figures are closed automatically
    after the processing step finishes."""
    import matplotlib._pylab_helpers as _helpers
    nr_of_active_windows = _helpers.Gcf.get_num_fig_managers()
    assert nr_of_active_windows == 0, "Some windows are still active."


def comparison_step_with_figure(simulations: process.SimulationsData):
    """Used to check whether figures are closed automatically
    after the processing step finishes."""
    _, _ = _plt.subplots(2, 1)
    _, _ = _plt.subplots(2, 1)


def comparison_step_with_figure_shown(simulation: process.Simulation):
    """Used to check whether figures are closed automatically
    after the processing step finishes."""
    import matplotlib._pylab_helpers as _helpers
    nr_of_active_windows = _helpers.Gcf.get_num_fig_managers()
    assert nr_of_active_windows == 0, "Some windows are still active."


class TestProcessingClosesFigures:
    """These tests check whether active figure managers exist in
    a step following a step with a figure.
    """
    scenario = [
                processing_step_with_figure,
                processing_step_with_figure,
                processing_step_with_figure_shown,
            ]
    comparison_scenario = [comparison_step_with_figure,
                           comparison_step_with_figure,
                           comparison_step_with_figure_shown,
                           ]

    def test_process_single_simulation(self, caplog):
        sim_folder = RESULTS_FOLDER / "sim-1"

        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.ERROR):
                return process.process_single_simulation(sim_folder, self.scenario)

        # first pass reading from raw files
        run_with_caplog()
        assert "Some windows are still active." not in caplog.text

    def test_process_whole_results_set(self, caplog):
        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.ERROR):
                return process.process_whole_result_set(RESULTS_FOLDER, self.scenario)

        # first pass reading from raw files
        run_with_caplog()
        assert "Some windows are still active." not in caplog.text

    def test_process_whole_results_set_parallel(self, caplog):
        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.INFO):
                return process.process_whole_result_set_parallel(RESULTS_FOLDER, self.scenario)

        # first pass reading from raw files
        run_with_caplog()
        assert "processing_step_with_figure_shown" not in caplog.text

    def test_do_comparison(self, caplog):
        def run_with_caplog():
            caplog.clear()
            with caplog.at_level(_logging.ERROR):
                return process.do_comparison(self.comparison_scenario, results_folder=RESULTS_FOLDER)

        # first pass reading from raw files
        run_with_caplog()
        assert "Some windows are still active." not in caplog.text


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
