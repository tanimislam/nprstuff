========
nprstuff
========

I like NPR, so I made some scripts to download my favorite programs from
NPR. For now, I have something that downloads `Fresh
Air <http://www.npr.org/programs/fresh-air/>`__, `Wait Wait..Don’t Tell
Me <http://www.npr.org/programs/wait-wait-dont-tell-me/>`__, and `This
American Life <http://www.thisamericanlife.org/>`__. This package can
probably, straightforwardly be extended to other NPR and PRI programs.

Although this project started off as a way to download these three
programs, I have expanded it to include a grab bag of altogether
different types of functionalities. What remains the same? This
distribution consists mainly of executable python scripts.

I organize this document into the following sections: Core
Functionality, New Functionality, Graphics Functionality (in folders
``gui`` and ``gui2``), and a small section called Oldstuff.

Core Functionality
==================

This consists of functionality to grab episodes from `Fresh
Air <http://www.npr.org/programs/fresh-air/>`__, `Wait Wait..Don’t Tell
Me <http://www.npr.org/programs/wait-wait-dont-tell-me/>`__, and `This
American Life <http://www.thisamericanlife.org/>`__. These consist of
the following pieces of python code:

-  ``npr_utils.py`` contains common utilities to get the proper metadata
   for NPR programs, to name these media files in the proper date
   format, and to get the full paths to the
   `LibAV/FFMPEG <https://libav.org>`__ and
   `HandBrakeCLI <https://handbrake.fr/>`__ tools to create the NPR
   programs in m4a and mp3 formats (among other functionalities).

-  These four files handle NPR Fresh Air downloads: ``freshair.py``,
   ``freshair_crontab.py``, ``freshair_fix_crontab.py``, and
   ``freshair_by_year.py``.

   -  ``freshair.py`` is the main executable that downloads NPR Fresh
      Air episodes, converts them to m4a format, and then applies
      correct metadata. The help screen for this command line tool is
      here,

      ::

          Usage: freshair.py [options]

          Options:
            -h, --help         show this help message and exit
            --dirname=DIRNAME  Name of the directory to store the file. Default is
                               /mnt/media/freshair.
            --date=DATE        The date, in the form of "January 1, 2014." The default
                               is today's date, November 14, 2015.
            --debug            If chosen, run freshair.py in debug mode. Useful for
                               debugging :)

   -  ``freshair_crontab.py`` downloads an NPR Fresh Air episode on a
      given weekday. It should be called by a cron job that should be
      run every weekday.

   -  ``freshair_fix_crontab.py`` tries to re-download NPR Fresh Air
      episodes that may be incomplete – defined as shorter than 30
      minutes – and which are 90 days or older. This executable searches
      through the library of all NPR Fresh Air episodes, and tries to
      re-download older, possibly incomplete episodes.

   -  ``freshair_by_year.py`` downloads all the NPR Fresh Air episodes
      in a given year.

-  These four files handle NPR Wait Wait downloads: ``waitwait.py``,
   ``waitwait_realmedia.py``, ``waitwait_crontab.py``, and
   ``waitwait_by_year.py``.

   -  ``freshair.py`` is the main executable that downloads NPR Wait
      Wait episodes, converts them to m4a format, and then applies
      correct metadata. ``waitwait_realmedia.py`` is a python module
      that allows one to download NPR Wait Wait episodes older than
      2004, which are in
      `RealMedia <https://en.wikipedia.org/wiki/RealMedia>`__ format.
      The help screen for this command line tool is here,

      ::

          Usage: waitwait.py [options]

          Options:
            -h, --help         show this help message and exit
            --dirname=DIRNAME  Name of the directory to store the file. Default is
                               /mnt/media/waitwait.
            --date=DATE        The date, in the form of "January 1, 2014." The default
                               is last Saturday, November 14, 2015.
            --debugonly        If chosen, download the NPR XML data sheet for this Wait
                               Wait episode.

   -  ``waitwait_crontab.py`` downloads an NPR Wait Wait episode on a
      given Saturday. It should be called by a cron job that should be
      run every Saturday.

   -  ``waitwait_by_year.py`` downloads all the NPR Wait Wait episodes
      in a given year.

-  ``thisamericanlife.py`` *manually* downloads a given episode number
   of This American Life. This executable uses a custom online archive
   for older This American Life episodes that are described
   `here <http://www.dirtygreek.org/t/download-this-american-life-episodes>`__.
   The help screen for this command line tool is here,

   ::

       Usage: thisamericanlife.py [options]

       Options:
         -h, --help            show this help message and exit
         --episode=EPISODE     Episode number of This American Life to download.
                               Default is 150.
         --directory=DIRECTORY
                               Directory into which to download This American Life
                               episodes. Default is /mnt/media/thisamericanlife.
         --extra=EXTRASTUFF    If defined, some extra stuff in the URL to get a This
                               American Life episode.

New Functionality
=================

This consists of newer functionality that does not download NPR
episodes, nor can one straightforwardly modify them to download NPR
episodes. These consist of the following pieces of python code.

-  ``autoCropImage.py`` automatically crops image (png, jpeg, tiff,
   etc.) files to remove whitespace. The default whitespace color is
   ``white``. The help screen for this command line tool is here,

   ::

       Usage: autoCropImage.py [options]

       Options:
         -h, --help       show this help message and exit
         --input=INPUT    Name of the input file.
         --output=OUTPUT  Name of the output file. Optional.
         --color=COLOR    Name of the color over which to autocrop. Default is white.

-  ``convertImage.py`` uses the `CloudConvert REST
   API <https://cloudconvert.com/apiconsole>`__ to *smoothly and without
   pain points* convert and resize SVG images to PNG images of the same
   base name. The help screen for this command line tool is here,

   ::

       Usage: convertImage.py [options]

       Options:
         -h, --help           show this help message and exit
         --filename=FILENAME  Name of the input SVG file.
         --width=WIDTH        If defined, new width of the file. Optional

-  ``changedates.py`` changes the creation date of JPG and MOV files,
   that my Canon digital camera creates, by up and down one year. I
   created this tool because my Canon digital camera does not set the
   right year on the creation date for image files it creates. This
   caused problems when I uploaded those images to `Google
   Picasa <https://picasa.google.com/>`__ or
   `Google+ <https://plus.google.com/>`__. The help screen for this
   command line tool is here,

   ::

       Usage: changedates.py [options]

       Options:
         -h, --help         show this help message and exit
         --dirname=DIRNAME  Name of the directory to look for jpeg files.
         --movs             If chosen, process MOV files instead.
         --minus            If chosen, subtract a year from the files.

Graphics Functionality
======================

Oldstuff
========
