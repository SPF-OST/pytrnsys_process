import pathlib as _pl

from pytrnsys_process.headers import Headers


class TestHeaders:

    PATH_TO_RESULTS = _pl.Path(__file__).parent / "data/results"

    def test_init_headers(self):
        headers = Headers(self.PATH_TO_RESULTS)

        headers.init_headers()

        assert headers.header_index.get("QSnk60P") == [
            ("sim-1", "ENERGY_BALANCE_MO_60_TESS.Prt"),
            ("sim-2", "ENERGY_BALANCE_MO_60_TESS.Prt"),
        ]
        assert headers.header_index.get("QSnk417PauxEvap_kW") == [
            ("sim-2", "ENERGY_BALANCE_MO_HP_417.Prt")
        ]


class TestBenchmarkHeaders:
    """Initial test have shown multi threading is slower than single thread for this problem.
    Rerunning these tests requires a more comprehensive data set"""

    PATH_TO_RESULTS = _pl.Path(__file__).parent / "data/results"

    def test_init_headers_benchmark(self, benchmark):
        def init_headers():
            Headers(self.PATH_TO_RESULTS).init_headers()

        benchmark(init_headers)

    def test_init_headers_benchmark_multi_thread(self, benchmark):
        def init_headers():
            Headers(self.PATH_TO_RESULTS).init_headers_multi_thread()

        benchmark(init_headers)
