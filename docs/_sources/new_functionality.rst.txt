.. include:: urls.rst

.. _new_functionality_label:
	     
New Functionality
^^^^^^^^^^^^^^^^^^^
This consists of newer functionality that does not download NPR episodes, nor can one straightforwardly modify them to download NPR episodes.

.. _autoCropImage_label:

``autoCropImage``
==================
``autoCropImage`` automatically crops image (PNG_, JPEG_, TIFF_, etc.) and PDF_ files to remove whitespace. The default whitespace color is ``white``. The help screen for this command line tool is here,

.. code-block:: console

   usage: autoCropImage [-h] --input INPUT [--output OUTPUT] [--color COLOR] [--trans] [--newwidth NEWWIDTH] [--show]

   optional arguments:
     -h, --help           show this help message and exit
     --input INPUT        Name of the input file.
     --output OUTPUT      Name of the output file. Optional.
     --color COLOR        Name of the color over which to autocrop. Default is white.
     --trans              If chosen, also remove the transparency wrapping around the image. Works only for non-PDF images.
     --newwidth NEWWIDTH  New width of the image.
     --show               If chosen, then show the final image after cropped.

.. _convertImage_label:

``convertImage``
================
``convertImage`` uses the `CloudConvert REST API`_ to *smoothly and without pain points* convert and resize SVG_ images to PNG_ images of the same base name. The help screen for this command line tool is here,

.. code-block:: console

   Usage: convertImage [options]

   Options:
     -h, --help           show this help message and exit
     --filename=FILENAME  Name of the input SVG file.
     --width=WIDTH        If defined, new width of the file. Optional

.. _changedates_label:

``changedates``
================
``changedates`` changes the creation date of JPEG_ and MOV_ files, that my Canon digital camera creates, by up and down one year. I created this tool because my Canon digital camera does not set the right year on the creation date for image files it creates. This caused problems when I uploaded those images to `Google Picasa <https://picasaweb.google.com/home>`__ or `Google+ <https://plus.google.com/>`__. The help screen for this command line tool is here,

.. code-block:: console

   usage: changedates [-h] --dirname DIRNAME [--movs] [--minus]

   optional arguments:
     -h, --help         show this help message and exit
     --dirname DIRNAME  Name of the directory to look for jpeg files.
     --movs             If chosen, process MOV files instead.
     --minus            If chosen, subtract a year from the files.

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

``myrst2html``
=================
``myrst2html`` acts *almost* like rst2html_ in default mode, except instead of using (for LaTeX math formulae) the ``math.css`` default it uses MathJax_ with the correct CDN_, which in this case is https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML. I borrow shamelessly from `this GitHub gist`_ with some slight modifications.

One uses it *just* like default rst2html_,

.. code-block:: console

   myrst2html filename.rst > filename.html

This generates the HTML file, ``filename.html``, from the RST markup file, ``filename.rst``, but now with MathJax_.
   
.. _rst2html: https://manpages.debian.org/testing/docutils-common/rst2html.1.en.html
.. _MathJax: https://www.mathjax.org/
.. _CDN: https://en.wikipedia.org/wiki/Content_delivery_network
.. _`this GitHub gist`: https://gist.github.com/Matherunner/c0397ae11cc72f2f35ae
