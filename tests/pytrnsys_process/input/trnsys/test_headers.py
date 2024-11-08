import pathlib as _pl

from pytrnsys_process.input.trnsys.Headers import Headers


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
