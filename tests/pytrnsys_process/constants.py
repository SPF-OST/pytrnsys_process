import pathlib as _pl

import pytrnsys_process as pp

REPO_ROOT = _pl.Path(pp.__file__).parents[1]
DATA_FOLDER = REPO_ROOT / "tests" / "pytrnsys_process" / "data"


