.. image:: https://badges.gitter.im/nprstuff-tanimislam/Lobby.svg
   :target: https://gitter.im/nprstuff-tanimislam/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=body_badge

###################################################################
Nprstuff - Utility Functionality for NPR Programs and Other Things
###################################################################
I like NPR, so I made some scripts to download my favorite programs from NPR. For now, I have something that downloads `NPR Fresh Air`_, `Wait Wait...Don't Tell
Me <waitwait_>`_, and `This American Life`_. This package can probably, straightforwardly be extended to other NPR and PRI programs (although I haven't yet done so).

Although this project started off as a way to download these three programs, I have expanded it to include a grab bag of altogether different types of functionalities. What remains the same? This distribution consists mainly of executable Python scripts. Detailed documentation lives in the Sphinx repository

NPR changed their API, which means that old functionality does not work. NPR has discontinued the `older NPR API`_, that powers much of this repository's functionality. I quote,

  This API is no longer publicly available for client integrations; for documentation of current API services, please visit the NPR Developer Center.

Furthermore, the newer `NPR One API`_ does not appear to have the necessary functionality to make my magic happen. The rest of the functionality lives in the

The comprehensive documentation lives in HTML created with `Sphinx <https://www.sphinx-doc.org/en/master/>`_, and now in the `Read the Docs <nprstuff_>`_ page for this project. To generate the documentation, go to the ``docs`` subdirectory. In that directory, run ``make html``. Load ``docs/build/html/index.html`` into a browser to see the documentation.

Installation Instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^

Installing this Python module is easy.

* If you want to get it from Github_, then run this command,

  .. code-block:: console

     python3 -m pip install --user git+https://github.com/tanimislam/nprstuff#egginfo=nprstuff

* If you want to have more control, follow these several steps.

  .. code-block:: console

     git clone https://github.com/tanimislam/nprstuff
     cd nprstuff
     python3 -m pip install --user -e .

Both installation workflows install ``nprstuff`` into your user Python folder (``~/.local`` by default on Linux and Mac OS X systems). Its executables are installed into ``~/.local/bin`` by default on Linux or Mac OS X systems.

.. _`NPR Fresh Air`: https://freshair.npr.org
.. _waitwait: https://waitwait.npr.org
.. _`This American Life`: https://www.thisamericanlife.org
.. _LibAV: https://libav.org
.. _FFMPEG: https://ffmpeg.org
.. _HandBrakeCLI: https://handbrake.fr
.. _`older NPR API`: https://www.npr.org/api/index
.. _`NPR One API`: https://dev.npr.org/api
.. _nprstuff: https://nprstuff.readthedocs.io
.. _M4A: https://en.wikipedia.org/wiki/MPEG-4_Part_14
.. _MP3: https://en.wikipedia.org/wiki/MP3
.. _RealMedia: https://en.wikipedia.org/wiki/RealMedia
.. _`CloudConvert REST API`: https://cloudconvert.com/apiconsole
.. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
.. _JPEG: https://en.wikipedia.org/wiki/JPEG
.. _TIFF: https://en.wikipedia.org/wiki/TIFF
.. _PDF: https://en.wikipedia.org/wiki/PDF
.. _MOV: https://en.wikipedia.org/wiki/QuickTime_File_Format
.. _OGG: https://en.wikipedia.org/wiki/Vorbis
.. _FLAC: https://en.wikipedia.org/wiki/FLAC
.. _SVG: https://en.wikipedia.org/wiki/Scalable_Vector_Graphics
.. _`Abdur-Rashid Sufi`: http://quranicaudio.com/quran/109
.. _Readability: https://www.readability.com
.. _PyQt4: https://www.riverbankcomputing.com/software/pyqt/download
.. _EPUB: https://en.wikipedia.org/wiki/EPUB
.. _Github: https://github.com
..
.. these are magazine URLS
..

.. _`Lightspeed Magazine`: http://www.lightspeedmagazine.com
.. _Medium: https://medium.com/>
.. _`The New Yorker`: https://www.newyorker.com
.. _`The New York Times`: https://www.nytimes.com
.. _`Virginia Quarterly Review`: https://www.vqronline.org
