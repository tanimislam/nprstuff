.. include:: urls.rst

Core Functionality
^^^^^^^^^^^^^^^^^^^

This consists of functionality to grab episodes from `Fresh Air`_, `Wait Wait..Don't Tell Me <waitwait_>`_, and `This American Life`_. ``npr_utils.py`` contains common utilities to get the proper metadata for NPR programs, to name these media files in the proper date format, and to get the full paths to the LibAV_ or FFMPEG_ and HandBrakeCLI_ tools used to create the NPR programs in M4A_ and MP3_ formats (among other functionalities).

NPR Fresh Air
==============
These four executables handle `NPR Fresh Air`_ downloads: ``freshair``, ``freshair_crontab``, ``freshair_fix_crontab``, and ``freshair_by_year``.
  
freshair
---------

``freshair`` is the main executable that downloads `NPR Fresh Air`_ episodes, converts them to M4A_ format, and then applies correct metadata. The help screen for this command line tool is here,

.. code-block::  console

    usage: freshair [-h] [--dirname DIRNAME] [--date DATE] [--mp3exist] [--debug]

    optional arguments:
      -h, --help         show this help message and exit
      --dirname DIRNAME  Name of the directory to store the file. Default is /mnt/media/freshair.
      --date DATE        The date, in the form of "January 1, 2014." The default is today's date, August 11, 2020.
      --mp3exist         If chosen, then do not download the transitional mp3 files. Use the ones that already exist.
      --debug            If chosen, run freshair.py in debug mode. Useful for debugging :)


freshair_crontab
-----------------
      
``freshair_crontab`` downloads an `NPR Fresh Air`_ episode on a given weekday. It should be called by a cron job or a systemd service that runs every weekday.

freshair_fix_crontab
---------------------

``freshair_fix_crontab`` tries to re-download `NPR Fresh Air`_ episodes that may be incomplete – defined as shorter than 30 minutes – and which are 90 days or older. This executable searches through the library of all NPR Fresh Air episodes, and tries to re-download older, possibly incomplete episodes.

freshair_by_year
------------------  

``freshair_by_year`` downloads all the NPR Fresh Air episodes in a given year. The help screen for this command line tool is here,

.. code-block:: console

   usage: freshair_by_year [-h] [--year YEAR] [--inputdir INPUTDIR] [--quiet] [--coverage] [--audit]

   optional arguments:
     -h, --help           show this help message and exit
     --year YEAR          Year in which to write out all Fresh Air episodes. Default is 2020.
     --inputdir INPUTDIR  Directory into which to store the NPR Fresh Air episodes. Default is /mnt/media/freshair.
     --quiet              If chosen, do not print verbose output from the action of this script. By default this is false.
     --coverage           If chosen, just give the list of missing Fresh Air episodes and nothing else.
     --audit              If chosen, do the audit picture here.

NPR Wait Wait
==============
These four executables handle `NPR Wait Wait <waitwait_>`_ downloads: ``waitwait``, ``waitwait_realmedia``, ``waitwait_crontab``, and ``waitwait_by_year``.

waitwait
---------

``waitwait`` is the main executable that downloads NPR Wait Wait episodes, converts them to M4A_ format, and then applies correct metadata. ``waitwait_realmedia.py`` is a Python module that allows one to download `NPR Wait Wait <waitwait_>`_ episodes older than 2004, which are in RealMedia_ format. The help screen for this command line tool is here,

.. code-block:: console

   usage: waitwait [-h] [--dirname DIRNAME] [--date DATE] [--debugonly] [--noverify] [--justfix]

   optional arguments:
     -h, --help         show this help message and exit
     --dirname DIRNAME  Name of the directory to store the file. Default is /mnt/media/waitwait.
     --date DATE        The date, in the form of "January 1, 2014." The default is last Saturday, August 08, 2020.
     --debugonly        If chosen, download the NPR XML data sheet for this Wait Wait episode.
     --noverify         If chosen, Do not verify the SSL connection.
     --justfix          If chosen, just fix the title of an existing NPR Wait Wait episode's file.

waitwait_crontab
-----------------

``waitwait_crontab`` downloads an NPR Wait Wait episode on a given Saturday. It should be called by a cron job or systemd service that is run every Saturday.

waitwait_by_year
------------------

``waitwait_by_year`` downloads all the NPR Wait Wait episodes in a given year. The help screen for this command line tool is here,

.. code-block:: console

   usage: waitwait_by_year [-h] [--year YEAR] [--inputdir INPUTDIR] [--quiet]

   optional arguments:
     -h, --help           show this help message and exit
     --year YEAR          Year in which to write out all Fresh Air episodes. Default is 2010.
     --inputdir INPUTDIR  Directory into which to store the NPR Fresh Air episodes. Default is /mnt/media/waitwait.
     --quiet              If chosen, do not print verbose output from the action of this script. By default this is false.

This American Life
===================

The executable ``thisamericanlife`` *manually* downloads a given episode number of `This American Life`_. The help screen for this command line tool is here,

.. code-block:: console

   usage: thisamericanlife [-h] [--episode EPISODE] [--directory DIRECTORY] [--extra EXTRASTUFF] [--noverify] [--dump] [--info]

   optional arguments:
     -h, --help            show this help message and exit
     --episode EPISODE     Episode number of This American Life to download. Default is 150.
     --directory DIRECTORY
			   Directory into which to download This American Life episodes. Default is /mnt/media/thisamericanlife.
     --extra EXTRASTUFF    If defined, some extra stuff in the URL to get a This American Life episode.
     --noverify            If chosen, then do not verify the SSL connection.
     --dump                If chosen, just download the TAL episode XML into a file into the specified directory.
     --info                If chosen, then do INFO logging.
