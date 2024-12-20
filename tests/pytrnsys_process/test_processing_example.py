from examples.ready_to_run import processing_example as pe
from pytrnsys_process import api

from tests.pytrnsys_process import constants as const


def test_processing_example_is_working_as_expected(caplog, monkeypatch):
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    monkeypatch.setattr(
        "pytrnsys_process.utils.convert_svg_to_emf", lambda x: None
    )
    data_path = const.REPO_ROOT / "examples/ready_to_run/data/results"

    processing_scenarios = [
        pe.processing_of_monthly_data,
        pe.processing_of_hourly_data,
    ]

    (
        api.process_whole_result_set(
            data_path,
            processing_scenarios,
        )
    )
    (
        api.process_single_simulation(
            data_path / "complete-0-SnkScale0.6000-StoreScale8",
            pe.processing_for_histogram,
        )
    )

    assert not any(record.levelname == "ERROR" for record in caplog.records)
