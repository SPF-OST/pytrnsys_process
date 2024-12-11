[![Coverage Status](https://coveralls.io/repos/github/SPF-OST/pytrnsys_process/badge.svg)](https://coveralls.io/github/SPF-OST/pytrnsys_process)

Post processing for `pytrnsys`.

You can finde the documentation here: https://pytrnsys-process.readthedocs.io/en/latest/

To find a running example, please refer to the `examples` folder.

```commandline 
py -3.12 -m venv venv 
venv\Scripts\python -m pip install pip==24.2
venv\Scripts\python -m pip install wheel
venv\Scripts\python -m pip install -r .\requirements\dev.txt
```

### Benchmarking tests:
```commandline
pytest --benchmark-only
pytest --benchmark-skip
```

