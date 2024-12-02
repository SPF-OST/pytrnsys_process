import pandas as _pd
import pytest as _pt

import tests.pytrnsys_process.constants as const
from pytrnsys_process.process_sim import process_file as pf
from pytrnsys_process.process_sim import process_sim as ps

PATH_TO_RESULTS = const.DATA_FOLDER / "results/sim-1"


class TestProcessSim:

    def test_process_sim_using_file_name_prt(self):
        simulation = ps.process_sim_prt(PATH_TO_RESULTS)

        self.do_assert(simulation)

    def test_process_sim_using_file_name_csv(self):
        simulation = ps.process_sim_csv(PATH_TO_RESULTS)

        self.do_assert(simulation)

    @_pt.mark.skip(reason="Skipped until step file requirements are clear")
    def test_process_sim_using_file_content_prt(self):
        simulation = ps.process_sim_using_file_content_prt(PATH_TO_RESULTS)

        self.do_assert(simulation)

    def do_assert(self, simulation):
        assert simulation.hourly.shape == (3, 18)
        assert simulation.monthly.shape == (14, 11)
        assert simulation.step.shape == (3, 9)


class TestProcessFile:

    def do_assert(self, simulation):
        expected_file_names = [
            "control_hr.prt",
            "ENERGY_BALANCE_MO_60_TESS.Prt",
            "ENERGY_BALANCE_MO_HP_225.Prt",
            "ENERGY_BALANCE_MO_HP_60.Prt",
            "PCMOut.hr",
            "sink_storage_temperatures_step.prt",
            "Src_Hr.Prt",
        ]
        for file in simulation.files:
            assert file.name in expected_file_names
        assert len(simulation.files) == 7

    def test_process_file_using_file_name(self):
        simulation = pf.process_simulation(PATH_TO_RESULTS)

        self.do_assert(simulation)

    def test_process_file_using_file_content(self):
        simulation = pf.process_simulation(
            PATH_TO_RESULTS, detect_file_using_content=True
        )

        self.do_assert(simulation)


class TestHandleDuplicateColumns:
    def test_handle_with_matching_duplicates(self):
        """Test merging when same column appears in multiple DataFrames."""
        df1 = _pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = _pd.DataFrame({"A": [1, 2], "C": [5, 6]})
        df3 = _pd.DataFrame({"A": [1, 2], "D": [7, 8]})

        result = ps.handle_duplicate_columns(
            _pd.concat([df1, df2, df3], axis=1)
        )

        expected = _pd.DataFrame(
            {"A": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]}
        )
        _pd.testing.assert_frame_equal(result, expected)

    def test_handle_with_conflicting_duplicates(self):
        """Test that conflicting values in duplicate columns raise ValueError."""
        df1 = _pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = _pd.DataFrame({"A": [1, 2], "C": [5, 6]})
        df3 = _pd.DataFrame({"A": [3, 2], "D": [7, 8]})

        with _pt.raises(
            ValueError,
            match="Column 'A' has conflicting values at same indices",
        ):
            ps.handle_duplicate_columns(_pd.concat([df1, df2, df3], axis=1))

    def test_handle_with_matching_none_duplicates(self):
        """Test merging of duplicate columns with null values."""
        df1 = _pd.DataFrame({"A": [None, 2], "B": [3, 4]})
        df2 = _pd.DataFrame({"A": [None, 2], "C": [5, 6]})
        df3 = _pd.DataFrame({"A": [None, 2], "C": [5, 6]})

        result = ps.handle_duplicate_columns(
            _pd.concat([df1, df2, df3], axis=1)
        )

        expected = _pd.DataFrame({"A": [None, 2], "B": [3, 4], "C": [5, 6]})
        _pd.testing.assert_frame_equal(result, expected)

    def test_handle_with_conflicting_none_duplicates(self):
        """Test merging of duplicate columns with null values."""
        df1 = _pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        df2 = _pd.DataFrame({"A": [1, 2], "C": [5, 6]})
        df3 = _pd.DataFrame({"A": [None, 2], "C": [5, 6]})

        with _pt.raises(
            ValueError,
            match="Column 'A' has NaN values in one column while having actual values in another",
        ):
            ps.handle_duplicate_columns(_pd.concat([df1, df2, df3], axis=1))


class TestBenchmarkProcessSim:

    def test_process_per_sim_using_file_name_prt(self, benchmark):
        benchmark(ps.process_sim_prt, PATH_TO_RESULTS)

    def test_process_per_sim_using_file_name_csv(self, benchmark):
        benchmark(ps.process_sim_csv, PATH_TO_RESULTS)

    def test_process_per_sim_using_file_content_prt(self, benchmark):
        benchmark(ps.process_sim_using_file_content_prt, PATH_TO_RESULTS)

    def test_process_per_file_using_file_content(self, benchmark):
        benchmark(
            pf.process_simulation,
            PATH_TO_RESULTS,
            detect_file_using_content=True,
        )

    def test_process_per_file_using_file_name(self, benchmark):
        benchmark(pf.process_simulation, PATH_TO_RESULTS)
