import matplotlib as _mpl


def pytest_sessionstart(session):
    """
    Tkinter causes many problems on CI.
    This enforces a non-Tkinter backend.
    """
    _mpl.use("Agg")
