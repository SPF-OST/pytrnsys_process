from examples.ready_to_run import processing_example as pe


def test_processing_example_is_working_as_expected(caplog, monkeypatch):
    monkeypatch.setattr("matplotlib.pyplot.show", lambda: None)
    monkeypatch.setattr(
        "pytrnsys_process.util.convert_svg_to_emf", lambda x: None
    )
    pe.main()

    assert not any(record.levelname == "ERROR" for record in caplog.records)
