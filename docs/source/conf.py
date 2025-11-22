import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'NoteManager'
copyright = '2025, Rum'
author = 'Rum'
release = '1.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = []
language = 'ru'

html_theme = 'classic'
html_static_path = ['_static']

napoleon_google_docstring = True