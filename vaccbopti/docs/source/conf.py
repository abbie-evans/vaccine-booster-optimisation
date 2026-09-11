# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys
import sphinx

# Make the project root importable
sys.path.insert(0, os.path.abspath('../..'))

project = 'Vaccine Booster Optimisation'
copyright = '2026, Abbie Evans, An Mei Daniels, Bente Vissel, Monica Dewi & Kristijonas Raibuzis'
author = 'Abbie Evans, An Mei Daniels, Bente Vissel, Monica Dewi & Kristijonas Raibuzis'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.mathjax',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

# Autodoc defaults
if int(sphinx.__version__.split('.')[1]) < 8:
    autodoc_default_flags = [
        'members',
        'inherited-members',
    ]
else:
    autodoc_default_options = {
        'members': None,
        'inherited-members': None,
    }

master_doc = 'index'

templates_path = ['_templates']
exclude_patterns = []

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
