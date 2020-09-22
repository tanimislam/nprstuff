.. include:: urls.rst

================================================
Core APIs
================================================

This document describes the nprstuff core API, which provides the low-level back-end for the CLI front ends described in :ref:`Core Functionality` and :ref:`New Functionality`. These modules live under ``nprstuff.core``.

The most fundamental change, from the `older NPR API`, is the usage of webscraping (through Selenium_) and inference to craft responses that return stories for `NPR Fresh Air`_ and `NPR Wait Wait <waitwait_>`_ episodes. Here is a screenshot.

.. image:: images/waitwait_screenshot_ANNOTATED.png
   :width: 100%
   :align: center

To get `NPR Wait Wait <waitwait_>`_ episodes for 8 AUGUST 2020, one needs to put this URL into address bar of the Selenium_ headless browser,

.. code-block:: console

   https://www.npr.org/search?query=*&page=1&refinementList[shows]=Wait Wait...Don't Tell Me!&range[lastModifiedDate][min]=1596783600&range[lastModifiedDate][max]=1596870000&sortType=byDateAsc

This unwieldy process required a fair amount of trial and error to (mostly) work.

Second, I have redesigned the Python logging functionality in the following way,

* custom format of the logging output, formatted as ``'%(levelname)s %(module)s.%(funcName)s (%(lineno)d): %(message)s'``. See the `logging cookbook`_ for more information on what this format means.

* the :ref:`Core Functionality` command line tools have an extra argument flag, ``--level``, that specifies whether to print out logging output and the following debug levels: ``DEBUG``, ``INFO``, or ``ERROR``.
      
npr_utils module
---------------------------------
This module contains common utilities to get the proper metadata for NPR programs, to name these media files in the proper date format, and to get the full paths to the LibAV_ or FFMPEG_ and HandBrakeCLI_ tools used to create the NPR programs in M4A_ and MP3_ formats (among other functionalities).

.. automodule:: nprstuff.core.npr_utils
   :members:
		
autocrop_image module
------------------------------------
This module provides low-level functionality that implements automatic cropping of lossy (PNG_, JPEG_, TIFF_) and PDF_ images.

This PDF_ autocropping functionality is copied over from `this repo`_. That repository is based off `pdfcrop.pl`_ to calculate the BoundingBox_. This functionality requires a working ghostscript_ (using the ``gs`` executable) to calculate the bounding box, and the PyPDF2_ module to read and manipulate PDF_ files.

.. image:: https://upload.wikimedia.org/wikipedia/commons/2/2a/PDF_BOX_01.svg
   :width: 100%

Three methods -- :py:meth:`get_boundingbox <nprstuff.core.autocrop_image.get_boundingbox>`, :py:meth:`crop_pdf <nprstuff.core.autocrop_image.crop_pdf>`, and  :py:meth:`crop_pdf_singlepage <nprstuff.core.autocrop_image.crop_pdf_singlepage>` -- are the higher level hooks to the PDF_ autocropping functionality.

.. automodule:: nprstuff.core.autocrop_image
   :members:

convert_image module
-----------------------------------
This module provides the low-level functionality to use the CloudConvert_ API to convert PDF_, PNG_, and SVG_ images into a final PNG_ image, utility functions to create MP4_ movies from a sequence of images, and to create animated GIF_ files, and created square movies (useful for upload to Instagram_).

This module also requires :py:class:`QSvgRenderer <PyQt5.QtSvg.QSvgRenderer>` for some of its functionality. However, PyPI_ does not have Python bindings to QtSVG_. To install on an Ubuntu_ machine, you can *thoughts and prayers* these instructions

.. code-block:: console

   sudo apt install python3-pyqt5.qtsvg

There may be similar installation instructions on other Linux, Windows and Mac OS X machines.


.. automodule:: nprstuff.core.convert_image
   :members:

music_to_m4a module
----------------------
This module provides low-level functionality that converts other music formats (MP3_, OGG_, and FLAC_) into M4A_. It also contains functionality to fix M4A_ metadata.

.. automodule:: nprstuff.core.music_to_m4a
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

waitwait and waitwait_realmedia modules
-----------------------------------------
These two modules provide the low level functionality to process and download `NPR Wait Wait...Don't Tell Me <waitwait_>`_ episodes.Until a few months ago, the `older NPR API`_ existed and worked without issues, but because it was so successful it went away. I now try to fix functionality that is broken, but it is slow undocumented going -- hence, diffusion. This is just like my experience with the :ref:`freshair and freshair_by_year modules`.

.. note::

   The functionality for downloading RealMedia_ `NPR Wait Wait <waitwait_>`_ episodes, which lives in :py:mod:`waitwait_realmedia <nprstuff.core.waitwait_realmedia>`, has not been tested in *years*. This module is used to download Wait Wait episodes before 2006; it may no longer work!

.. automodule:: nprstuff.core.waitwait
   :members:

.. automodule:: nprstuff.core.waitwait_realmedia
   :members:

.. _CloudConvert: https://cloudconvert.com
.. _GIF: https://en.wikipedia.org/wiki/GIF
.. _PyPI: https://pypi.org
.. _Ubuntu: https://ubuntu.com
.. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
.. _RealMedia: https://en.wikipedia.org/wiki/RealMedia
.. _`logging cookbook`: https://docs.python.org/3/howto/logging-cookbook.html
.. _QtSVG: https://doc.qt.io/qt-5/qtsvg-index.html
.. _`this repo`: https://gist.github.com/jpscaletti/7321281
.. _BoundingBox: https://upload.wikimedia.org/wikipedia/commons/2/2a/PDF_BOX_01.svg
.. _ghostscript: https://www.ghostscript.com
.. _pdfcrop.pl: https://github.com/ho-tex/pdfcrop
.. _PyPDF2: https://mstamy2.github.io/PyPDF2
