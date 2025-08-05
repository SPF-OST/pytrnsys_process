import pandas as _pd
import pytest as _pt

import tests.pytrnsys_process.constants as const
from pytrnsys_process import util
from pytrnsys_process.process import process_sim as ps

PATH_TO_RESULTS = const.DATA_FOLDER / "process-sim" / "sim-1"
PATH_TO_RESULTS_2 = const.DATA_FOLDER / "process-sim" / "sim-2"


class TestProcessSim:

    def test_process_sim_prt(self, monkeypatch):
        if not PATH_TO_RESULTS.exists():
            raise FileNotFoundError("Files themselves not found.")

        monkeypatch.setattr(
            "pytrnsys_process.config.global_settings.reader.read_step_files",
            True,
        )
        sim_files = util.get_files([PATH_TO_RESULTS], get_mfr_and_t=True)
        simulation = ps.process_sim(sim_files, PATH_TO_RESULTS)

        log_file_path = PATH_TO_RESULTS / "processing.log"
        if not log_file_path.exists():
            raise FileNotFoundError("Log file not found.")
        
        with open(log_file_path, encoding="utf-8") as f:
            logging_text = f.read()

        assert (
            "don-not-process.xlsx: No columns to parse from file"
            in logging_text
        )
        self.do_assert(simulation)
        assert simulation.scalar.shape == (1, 10)

    def test_process_sim_csv(self, monkeypatch):
        sim_files = util.get_files(
            [PATH_TO_RESULTS],
            results_folder_name="converted",
            get_mfr_and_t=False,
        )
        monkeypatch.setattr(
            "pytrnsys_process.config.global_settings.reader.read_step_files",
            True,
        )
        simulation = ps.process_sim(sim_files, PATH_TO_RESULTS)
        self.do_assert(simulation)

    def test_process_sim_ignore_step(self, monkeypatch):
        sim_files = util.get_files([PATH_TO_RESULTS])
        monkeypatch.setattr(
            "pytrnsys_process.config.global_settings.reader.read_step_files",
            False,
        )
        simulation = ps.process_sim(sim_files, PATH_TO_RESULTS)
        assert simulation.step.shape == (0, 0)

    def test_process_sim_ignore_deck(self, monkeypatch):
        sim_files = util.get_files([PATH_TO_RESULTS])
        monkeypatch.setattr(
            "pytrnsys_process.config.global_settings.reader.read_deck_files",
            False,
        )
        simulation = ps.process_sim(sim_files, PATH_TO_RESULTS)
        assert simulation.scalar.shape == (0, 0)

    def test_process_sim_type_25_step(self, monkeypatch):
        monkeypatch.setattr(
            "pytrnsys_process.config.global_settings.reader.read_step_files",
            True,
        )
        sim_files = util.get_files(
            [PATH_TO_RESULTS_2], get_mfr_and_t=False, read_deck_files=False
        )
        simulation = ps.process_sim(sim_files, PATH_TO_RESULTS_2)

        assert simulation.step.shape == (5, 5)

    @staticmethod
    def do_assert(simulation):
        assert simulation.hourly.shape == (3, 18)
        assert simulation.monthly.shape == (14, 11)
        assert simulation.step.shape == (5, 142)


class TestProcessFile:

    def do_assert(self, simulation):
        expected_file_names = [
            "PySimCoolDownAdd_Mfr.prt",
            "PySimCoolDownAdd_T.prt",
            "ENERGY_BALANCE_MO_60_TESS.Prt",
            "ENERGY_BALANCE_MO_HP_60.Prt",
            "ModePrinter_step.prt",
            "Src_Hr.Prt",
            "control.prt",
            "ENERGY_BALANCE_HP_225.Prt",
            "HPCtrlPrinter.Prt",
            "PCMOut.prt",
        ]
        for file in simulation.files:
            assert file.name in expected_file_names


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

    def test_handle_with_conflicting_time_duplicates(self):
        """Test that conflicting values of the Time column are kicked out, when the import printer column is correct."""
        df1 = _pd.DataFrame({"Period": [1, 2], "Time": [1, 2], "B": [3, 4]})
        df2 = _pd.DataFrame({"Period": [1, 2], "Time": [1, 2], "C": [5, 6]})
        df3 = _pd.DataFrame({"Period": [1, 2], "Time": [3, 2], "D": [7, 8]})

        result = ps.handle_duplicate_columns(
            _pd.concat([df1, df2, df3], axis=1)
        )
        expected = _pd.DataFrame(
            {"Period": [1, 2], "B": [3, 4], "C": [5, 6], "D": [7, 8]}
        )
        _pd.testing.assert_frame_equal(result, expected)

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

    def test_process_per_sim_prt(self, benchmark):
        sim_files = util.get_files([PATH_TO_RESULTS])

        benchmark(lambda: ps.process_sim(sim_files, PATH_TO_RESULTS))

    def test_process_per_sim_csv(self, benchmark):
        sim_files = util.get_files([PATH_TO_RESULTS])

        benchmark(lambda: ps.process_sim(sim_files, PATH_TO_RESULTS))
