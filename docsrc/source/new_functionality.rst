.. include:: urls.rst

.. _new_functionality_label:
	     
New Functionality
^^^^^^^^^^^^^^^^^^^
This consists of newer functionality that does not download NPR episodes, nor can one straightforwardly modify them to download NPR episodes.

.. _convertImage_youtube_label:

``convertImage_youtube``
==========================
``convertImage_youtube`` converts a YouTube_ clip into an animated GIF_. It *first* creates an MP4_ file, and then converts that MP4_ file into an animated GIF_. Its help screen, when running ``convertImage_youtube -h``, is,

.. code-block:: console

   usage: convertImage_youtube [-h] [--noverify] [--info] -u url -o output
			       [-q quality] [-d duration] [-s scale]

   Creates an animated GIF from a YouTube clip!

   optional arguments:
     -h, --help            show this help message and exit
     --noverify            If chosen, do not verify the SSL connection.
     --info                If chosen, then print out INFO level logging.
     -u url, --url url     YouTube URL of the input video.
     -o output, --output output
			   Name of the output animated GIF file that will be
			   created.
     -q quality, --quality quality
			   The quality of the YouTube clip to download. Only
			   video portion is downloaded. May be one of highest,
			   high, medium, low. Default is highest.
     -d duration, --duration duration
			   Optional argument. If chosen, the duration (in
			   seconds, from beginning) of the video to be converted
			   into an animated GIF.
     -s scale, --scale scale
			   Optional scaling of the input video. Default is 1.0.
			   
The two required arguments are ``-u`` or ``--url`` (the YouTube_ URL of the input video), and ``-o`` or ``--output`` for the name of the output animated GIF_. There are five optional arguments,

* ``-q`` or ``--quality`` specifies the quality of the YouTube_ clip to download. May be one of ``highest``, ``high``, ``medium``, or ``low``. The default is ``highest``.

* ``-d`` or ``--duration`` specifies the duration (in seconds, from the beginning) of the video to convert into an animated GIF_. If you don't specify, then it will use the *whole* video.

* ``-s`` or ``--scale`` resizes the width and height of the intermediate MP4_ file by some number. Its default is 1.0, and it must be greater than zero.

* ``--info`` prints out :py:const:`INFO <logging.INFO>` level :py:mod:`logging` output.

* ``--noverify`` ignores verification of SSL transactions. It is optional and defaults to ``False``.

So for example, we take this `fun clip from the Lucas Bros. Moving Co. <https://www.youtube.com/watch?v=R-pmYwr8zbU>`_, which we show below,

.. youtube:: R-pmYwr8zbU
   :width: 100%

And run this command,

.. code-block:: console

   convertImage youtube -u "https://www.youtube.com/watch?v=R-pmYwr8zbU" -o "lucas_bros.gif" -q highest -s 0.5

to generate a ``highest`` quality animated GIF_, scaled to *half* the original size of the YouTube_ clip, into :numref:`lucas_bros_gif` (17M in size).

.. _lucas_bros_gif:

.. figure:: images/lucas_bros.gif
   :width: 100%
   :align: left

   One of my favorite scenes from `Lucas Bros. Moving Co. S01E03: Before & After Models <https://www.imdb.com/title/tt3472130/?ref_=ttep_ep3>`_. I giggle each time I see it.

.. _music_to_m4a_label:
     
``music_to_m4a``
=================
``music_to_m4a`` can convert a single file from MP3_, OGG_, or FLAC_ format to M4A_ format while preserving music file metadata, and can optionally set the total number of album tracks and the album cover if the music files is in an album. It can also rename an m4a music file into the format “*artist name* - *song name*.m4a.” The help screen for this command line tool is here,

.. code-block:: console

   usage: music_to_m4a [-h] --inputfile INPUTFILE [--outfile OUTFILE] [--tottracks TOTTRACKS] [--albumloc ALBUMLOC] [--quiet] [--rename] [--notitle]

   optional arguments:
     -h, --help            show this help message and exit
     --inputfile INPUTFILE
			   Name of the input audio file to convert.
     --outfile OUTFILE     Optional name of the output file.
     --tottracks TOTTRACKS
			   Optional total number of tracks in album of which song is a part.
     --albumloc ALBUMLOC   Optional path to location of the album cover image file. Must be in JPEG or PNG.
     --quiet               If chosen, then verbosely print output of processing.
     --rename              If chosen, simply rename the m4a file to the form <artist>.<song title>.m4a
     --notitle             If chosen, do not use titlecase functionality to fix the titles of songs.

.. _download_surahs_label:
     
``download_surahs``
====================
``download_surahs`` downloads recorded surahs (`Abdur-Rashid Sufi`_) to a directory of your choice. The help screen for this command line tool is here,

.. code-block:: console

   usage: download_surahs [-h] [--outdir OUTDIR]

   optional arguments:
     -h, --help       show this help message and exit
     --outdir OUTDIR  Directory to put this data into. Default is /mnt/software/sources/pythonics/nprstuff.

.. _rst2html: https://manpages.debian.org/testing/docutils-common/rst2html.1.en.html
.. _MathJax: https://www.mathjax.org/
.. _CDN: https://en.wikipedia.org/wiki/Content_delivery_network
.. _`this GitHub gist`: https://gist.github.com/Matherunner/c0397ae11cc72f2f35ae
.. _PNG: https://en.wikipedia.org/wiki/Portable_Network_Graphics
.. _PDF: https://en.wikipedia.org/wiki/PDF
.. _`git bisect`: https://git-scm.com/docs/git-bisect
.. _GIF: https://en.wikipedia.org/wiki/GIF
.. _YouTube: https://www.youtube.com
.. _FFmpeg: https://ffmpeg.org
.. _movie_2_gif: http://blog.pkh.me/p/21-high-quality-gif-with-ffmpeg.html
.. _SVG: https://en.wikipedia.org/wiki/Scalable_Vector_Graphics
.. _SVGZ: https://en.wikipedia.org/wiki/Scalable_Vector_Graphics#Compression
.. _pdftocairo: http://manpages.ubuntu.com/manpages/trusty/man1/pdftocairo.1.html
.. _cairosvg: http://manpages.ubuntu.com/manpages/focal/en/man1/cairosvg.1.html
.. _MP4: https://en.wikipedia.org/wiki/MPEG-4_Part_14
.. _`Medium article`: https://medium.com/@Peter_UXer/small-sized-and-beautiful-gifs-with-ffmpeg-25c5082ed733
