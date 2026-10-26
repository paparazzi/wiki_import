"""Standalone Paparazzi UAV hardware documentation."""

project = 'Paparazzi UAV Hardware'
author = 'Paparazzi UAV Team'
copyright = 'Paparazzi UAV Team'

extensions = ['myst_parser']
source_suffix = {'.rst': 'restructuredtext', '.md': 'markdown'}
master_doc = 'index'
language = 'en'
myst_enable_extensions = ['colon_fence']
myst_heading_anchors = 3

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']
