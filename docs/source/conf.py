# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os, sys, datetime
from functools import reduce
from sphinx.util import logging
_mainDir = reduce(lambda x,y: os.path.dirname( x ),
                  range(2), os.path.abspath('.'))
sys.path.insert( 0, _mainDir )

is_in_readthedocs = ( os.environ.get( 'READTHEDOCS' ) is not None )

logger = logging.getLogger( __name__ )
logger.info( "mainDir = %s" % _mainDir)
logger.info( 'READTHEDOCS: %s.' % os.environ.get('READTHEDOCS') )

#
## now don't verify the TLS if not in READTHEDOCS
tls_verify = is_in_readthedocs

#
## numfig stuff
numfig = True

# -- Project information -----------------------------------------------------

project = 'nprstuff'
copyright = '2020, Tanim Islam'
author = 'Tanim Islam'

# The full version, including alpha/beta/rc tags
release = '1.0'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.mathjax',
    'sphinx.ext.autosectionlabel',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
    'sphinx.ext.napoleon',
    'sphinx.ext.todo',
    'sphinx_issues',
    'sphinxarg.ext'
]

#
## following instructions here (https://github.com/svenevs/exhale/tree/master/docs/_intersphinx) to fix beautifulsoup doc.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'requests': ( 'https://requests.kennethreitz.org/en/master/', None),
    'beautifulsoup' : ( 'https://www.crummy.com/software/BeautifulSoup/bs4/doc/', None ), # "_intersphinx/bs4_objects.inv"),
    'selenium' : ( 'https://selenium-python.readthedocs.io', None ),
    'pyqt5' : ( 'https://www.riverbankcomputing.com/static/Docs/PyQt5', None ), # "_intersphinx/pyqt5_objects.inv" ),
    'PyPDF2' : ( 'https://pythonhosted.org/PyPDF2', None ),
    'Pillow' : ( 'https://pillow.readthedocs.io/en/stable', None ),
}


# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

#
# source_suffix = ['.rst', '.md']
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'
html_sidebars = {
   '**': ['globaltoc.html', 'sourcelink.html', 'searchbox.html'],
   'using/windows': ['windowssidebar.html', 'searchbox.html'],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'
