# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import pathlib as pl
import sys
from datetime import datetime

_REPO_ROOT_DIR_PATH_STRING = str(pl.Path(__file__).parents[1])
if _REPO_ROOT_DIR_PATH_STRING not in sys.path:
    sys.path.insert(0, _REPO_ROOT_DIR_PATH_STRING)

project = "pytrnsys_process"
copyright = f"{datetime.now().year}, SPF Institute of Solar Technology, OST University of Applied Sciences"
author = "SPF Institute of Solar Technology, OST University of Applied Sciences"
version = "0.1"  # The short X.Y version
release = "0.1.0"  # The full version, including alpha/beta/rc tags

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Sphinx core extensions
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    # External extensions
    "sphinx_gallery.gen_gallery",
    "numpydoc",  # Better docstring support
    "IPython.sphinxext.ipython_console_highlighting",
    "IPython.sphinxext.ipython_directive",
]

# Configure sphinx-gallery
sphinx_gallery_conf = {
    'examples_dirs': [
        '../galleries/tutorials',  # path to tutorial scripts
        '../galleries/examples',  # path to example scripts
    ],
    'gallery_dirs': [
        'gen_tutorials',  # path where to save generated tutorials
        'gen_examples',  # path where to save generated examples
    ],
    'filename_pattern': r'(?:plot_|tutorial_)',  # Include files starting with 'plot_' or 'tutorial'
    'plot_gallery': 'True',  # Generate plots for examples
    'thumbnail_size': (400, 400),  # Size of thumbnails
    'remove_config_comments': True,
    'min_reported_time': 0,
}

# Configure autodoc
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__'
}

# Configure numpydoc
numpydoc_show_class_members = False
numpydoc_use_plots = True

# Configure intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'matplotlib': ('https://matplotlib.org/stable/', None),
}

# Configure doctest
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

html_theme = "pydata_sphinx_theme"

# Add GitHub repository information
html_context = {
    "github_user": "SPF-OST",
    "github_repo": "pytrnsys_process",
    "github_version": "main",  # The branch name
    "doc_path": "doc",  # The path to the documentation within the repository
}

html_theme_options = {
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/SPF-OST/pytrnsys_process",
            "icon": "fab fa-github-square",
        },
    ],
    "use_edit_page_button": True,
    "show_toc_level": 2,
    "navbar_align": "left",
    "navbar_end": ["navbar-icon-links", "theme-switcher"],
    "footer_items": ["copyright", "sphinx-version", "theme-version"],
}

html_static_path = ['_static']
html_css_files = ['custom.css']

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
html_logo = "_static/spf-logo.svg"  # Add your logo path here if you have one

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
html_favicon = None  # Add your favicon path here if you have one
