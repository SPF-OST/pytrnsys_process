# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathlib as pl
import sys

_REPO_ROOT_DIR_PATH_STRING = str(pl.Path(__file__).parents[1])
if _REPO_ROOT_DIR_PATH_STRING not in sys.path:
    sys.path.insert(0, _REPO_ROOT_DIR_PATH_STRING)

project = "pytrnsys_process"
copyright = "2024, SPF Institute of Solar Technology, OST University of Applied Sciences"
author = (
    "SPF Institute of Solar Technology, OST University of Applied Sciences"
)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
]

doctest_test_doctest_blocks = "yes"

doctest_global_setup = """\
import pandas as pd
pd.set_option('display.max_columns', 5)
pd.set_option('display.width', 80)
"""

trim_doctest_flags = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"

html_theme_options = {
    "page_width": "95%",
}
