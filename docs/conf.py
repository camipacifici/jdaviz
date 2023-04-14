# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst
#
# Astropy documentation build configuration file.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# Note that not all possible configuration values are present in this file.
#
# All configuration values have a default. Some values are defined in
# the global Astropy configuration which is loaded here before anything else.
# See astropy.sphinx.conf for which values are set there.

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
# sys.path.insert(0, os.path.abspath('..'))
# IMPORTANT: the above commented section was generated by sphinx-quickstart, but
# is *NOT* appropriate for astropy or Astropy affiliated packages. It is left
# commented out with this explanation to make it clear why this should not be
# done. If the sys.path entry above is added, when the astropy.sphinx.conf
# import occurs, it will import the *source* version of astropy instead of the
# version installed (if invoked as "make html" or directly with sphinx), or the
# version in the build directory (if "python setup.py build_sphinx" is used).
# Thus, any C-extensions that are needed to build the documentation will *not*
# be accessible, and the documentation will not build correctly.

import os
import sys
import datetime
import importlib.metadata as importlib_metadata

try:
    from sphinx_astropy.conf.v1 import *  # noqa
except ImportError:
    print('ERROR: the documentation requires the sphinx-astropy package to be installed')
    sys.exit(1)

# Get configuration information from setup.cfg
from configparser import ConfigParser
conf = ConfigParser()

conf.read(os.path.join(os.pardir, 'setup.cfg'))
setup_cfg = conf['metadata']

# -- General configuration ----------------------------------------------------

# By default, highlight as Python 3.
highlight_language = 'python3'

# If your documentation needs a minimal Sphinx version, state it here.
#needs_sphinx = '1.2'

# To perform a Sphinx version check that needs to be more specific than
# major.minor, call `check_sphinx_version("x.y.z")` here.
# check_sphinx_version("1.2.1")

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns.append('_templates')

# This is added to the end of RST files - a good place to put substitutions to
# be used globally.
rst_epilog += """
.. |icon-white-to-black| image:: /img/icons/white_to_black.png
  :scale: 80
  :alt: white to black icon

.. |icon-blink| image:: /img/icons/blink.png
  :scale: 80
  :alt: blink icon

.. |icon-plus| image:: /img/icons/picture_with_plus.png
  :scale: 40
  :alt: picture with a plus icon

.. |icon-plugins| image:: /img/icons/plugins.png
  :scale: 40
  :alt: plugins icon

.. |icon-settings-sliders| image:: /img/icons/settings_sliders.png
  :scale: 40
  :alt: settings sliders icon

.. |icon-zoom-pan-home| image:: /img/icons/zoom_pan_home.png
  :scale: 40
  :alt: reset zoom/pan icon

.. |icon-zoom-pan-2d| image:: /img/icons/zoom_pan_2d.png
  :scale: 40
  :alt: 2D zoom/pan icon

.. |icon-zoom-pan-horiz| image:: /img/icons/zoom_pan_horiz.png
  :scale: 40
  :alt: horizontal zoom/pan icon

.. |icon-zoom-pan-vert| image:: /img/icons/zoom_pan_vert.png
  :scale: 40
  :alt: vertical zoom/pan icon

.. |icon-region-horiz| image:: /img/icons/region_horiz.png
  :scale: 40
  :alt: horizontal region icon

.. |icon-region-circ| image:: /img/icons/region_circ.png
  :scale: 40
  :alt: circular region icon

.. |icon-eye| image:: /img/icons/eye.png
  :scale: 40
  :alt: eye icon

.. |icon-color-square| image:: /img/icons/color_square.png
  :scale: 40
  :alt: color square icon

.. |icon-box-zoom| image:: /img/icons/box_zoom.png
  :scale: 40
  :alt: box zoom icon

.. |icon-xrange-zoom| image:: /img/icons/xrange_zoom.png
  :scale: 40
  :alt: xrange zoom icon


.. |icon-line-select| image:: /img/icons/line_select.png
  :scale: 40
  :alt: line select icon


.. |icon-viewer-data-select| image:: /img/icons/viewer_data_select.png
  :scale: 30
  :alt: data select icon
"""

# -- Project information ------------------------------------------------------

# This does not *have* to match the package name, but typically does
project = setup_cfg['name']
author = setup_cfg['author']
copyright = '{0}, {1}'.format(
    datetime.datetime.now().year, author)

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.

# The full version, including alpha/beta/rc tags.
release = importlib_metadata.version(project)
# The short X.Y version.
version = '.'.join(release.split('.')[:2])

extensions += ['sphinx.ext.extlinks']
gh_tag = f'v{release}' if '.dev' not in release else 'main'
extlinks = {'gh-tree': (f'https://github.com/spacetelescope/jdaviz/tree/{gh_tag}/%s', '%s'),
            'gh-notebook': (f'https://github.com/spacetelescope/jdaviz/blob/{gh_tag}/notebooks/%s.ipynb',
                            '%s notebook')}

# -- Options for HTML output --------------------------------------------------

# A NOTE ON HTML THEMES
# The global astropy configuration uses a custom theme, 'bootstrap-astropy',
# which is installed along with astropy. A different theme can be used or
# the options for this theme can be modified by overriding some of the
# variables set in the global configuration. The variables set in the
# global configuration are listed below, commented out.


# Add any paths that contain custom themes here, relative to this directory.
# To use a different custom theme, add the directory containing the theme.
#html_theme_path = []

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes. To override the custom theme, set this to the
# name of a builtin theme or the name of a custom theme in html_theme_path.
#html_theme = None

html_theme = "sphinx_rtd_theme"

# Custom sidebar templates, maps document names to template names.
#html_sidebars = {}

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = ''

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = ''

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = ''

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = '{0} v{1}'.format(project, release)

# Output file base name for HTML help builder.
htmlhelp_basename = project + 'doc'


# -- Options for LaTeX output -------------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [('index', project + '.tex', project + u' Documentation',
                    author, 'manual')]


# -- Options for manual page output -------------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [('index', project.lower(), project + u' Documentation',
              [author], 1)]


# -- Options for the edit_on_github extension ---------------------------------

if setup_cfg.get('edit_on_github').lower() == 'true':

    extensions += ['sphinx_astropy.ext.edit_on_github']

    edit_on_github_project = setup_cfg['github_project']
    edit_on_github_branch = "main"

    edit_on_github_source_root = ""
    edit_on_github_doc_root = "docs"

# -- Resolving issue number to links in changelog -----------------------------
github_issues_url = 'https://github.com/{0}/issues/'.format(setup_cfg['github_project'])

# -- Turn on nitpicky mode for sphinx (to warn about references not found) ----
nitpicky = True

# Do not populate this if you use nitpick-exceptions below.
nitpick_ignore = []

# Some warnings are impossible to suppress, and you can list specific references
# that should be ignored in a nitpick-exceptions file which should be inside
# the docs/ directory. The format of the file should be:
#
# <type> <class>
#
# for example:
#
# py:class astropy.io.votable.tree.Element
# py:class astropy.io.votable.tree.SimpleElement
# py:class astropy.io.votable.tree.SimpleElementWithContent
#
# Uncomment the following lines to enable the exceptions:
#
for line in open('nitpick-exceptions'):
    if line.strip() == "" or line.startswith("#"):
        continue
    dtype, target = line.split(None, 1)
    target = target.strip()
    nitpick_ignore.append((dtype, target))

# Extra intersphinx in addition to what is already in sphinx-astropy
intersphinx_mapping['glue'] = ('http://docs.glueviz.org/en/stable/', None)
intersphinx_mapping['glue_jupyter'] = ('https://glue-jupyter.readthedocs.io/en/stable/', None)
intersphinx_mapping['regions'] = ('https://astropy-regions.readthedocs.io/en/stable/', None)
intersphinx_mapping['skimage'] = ('https://scikit-image.org/docs/stable/', None)
intersphinx_mapping['specutils'] = ('https://specutils.readthedocs.io/en/stable/', None)
intersphinx_mapping['specreduce'] = ('https://specreduce.readthedocs.io/en/stable/', None)
intersphinx_mapping['photutils'] = ('https://photutils.readthedocs.io/en/stable/', None)
intersphinx_mapping['traitlets'] = ('https://traitlets.readthedocs.io/en/stable/', None)
intersphinx_mapping['roman_datamodels'] = ('https://roman-datamodels.readthedocs.io/en/stable/', None)

# Options for linkcheck
linkcheck_ignore = ['https://github.com/spacetelescope/jdaviz/settings/branches']
