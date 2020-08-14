.. include:: urls.rst

================================================
Core APIs
================================================

This document describes the nprstuff core API, which provides the low-level back-end for the CLI front ends described in :ref:`Core Functionality` and :ref:`New Functionality`. These modules live under ``nprstuff.core``.

npr_utils module
---------------------------------
This module contains common utilities to get the proper metadata for NPR programs, to name these media files in the proper date format, and to get the full paths to the LibAV_ or FFMPEG_ and HandBrakeCLI_ tools used to create the NPR programs in M4A_ and MP3_ formats (among other functionalities).

.. automodule:: nprstuff.core.npr_utils
   :members:
		
autocrop_image module
------------------------------------
This module provides low-level functionality that implements automatic cropping of lossy (PNG_, JPEG_, TIFF_) and PDF_ images.

.. automodule:: nprstuff.core.autocrop_image
   :members:

convert_image module
-----------------------------------
This module provides the low-level functionality to use the CloudConvert_ API to convert PDF_, PNG_, and SVG_ images into a final PNG_ image, utility functions to create MP4_ movies from a sequence of images, and to create animated GIF_ files, and created square movies (useful for upload to Instagram_).

This module also requires :py:class:`QtSvgRenderer <PyQt5.QtSvg.QsvgRenderer>` for some of its functionality. However, PyPI_ does not have QtSvg. To install on an Ubuntu_ machine, you can *thoughts and prayers* these instructions

.. code-block:: console

   sudo apt install python3-pyqt5.qtsvg

There may be similar installation instructions on other Linux, Windows and Mac OS X machines.


.. automodule:: nprstuff.core.convert_image
   :members:


freshair and freshair_by_year modules
--------------------------------------
These two modules provide the low level functionality to process and download `NPR Fresh Air`_ episodes. Until a few months ago, the `older NPR API`_ existed and worked without issues, but because it was so successful it went away. I now try to fix functionality that is broken, but it is slow undocumented going -- hence, diffusion.

 .. automodule:: nprstuff.core.freshair
    :members:

 .. automodule:: nprstuff.core.freshair_by_year
    :members:

thisamericanlife module
-------------------------
This module provides the low level functionality to the :ref:`This American Life` CLI and some extra functionality.

.. automodule:: nprstuff.core.thisamericanlife
   :members:

waitwait and waitwait_by_year modules
--------------------------------------
These two modules provide the low level functionality to process and download `NPR Wait Wait...Don't Tell Me <waitwait_>`_ episodes.Until a few months ago, the `older NPR API`_ existed and worked without issues, but because it was so successful it went away. I now try to fix functionality that is broken, but it is slow undocumented going -- hence, diffusion. This is just like my experience with the :ref:`freshair and freshair_by_year modules`.

.. _CloudConvert: https://cloudconvert.com
.. _GIF: https://en.wikipedia.org/wiki/GIF
.. _PyPI: https://pypi.org
.. _Ubuntu: https://ubuntu.com
.. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
