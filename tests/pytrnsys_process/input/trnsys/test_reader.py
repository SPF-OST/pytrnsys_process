import pathlib as _pl

from pytrnsys_process.input.trnsys.readers import Reader


class TestReader:

    HOURLY_RESULTS = _pl.Path(__file__).parent / "data/hourly/Src_Hr.Prt"

    def test_read_hourly(self):
        Reader.read_hourly(self.HOURLY_RESULTS)
