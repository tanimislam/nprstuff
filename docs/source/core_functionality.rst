.. include:: urls.rst

Core Functionality
^^^^^^^^^^^^^^^^^^^
This consists of functionality to grab episodes from `NPR Fresh Air`_, `NPR Wait Wait..Don't Tell Me <waitwait_>`_, and `This American Life`_.

CONFIGURATION
==============
The command line tool ``nprconfig`` shows the following core functionality configuration settings.

* the NPR API key.
* The default download directory for `NPR Fresh Air`_ episodes.
* The default download directory for `NPR Wait Wait`_ episodes.

It has two modes of operation: ``show`` displays nprstuff core functionality settings; and ``set`` sets any or all of the three configuration settings. The top level help is,

.. code-block:: console

   usage: nprconfig [-h] [--level {DEBUG,ERROR,INFO,NONE}] {show,set} ...

   positional arguments:
     {show,set}            Choose one of these options: (show) shows the NPR core functionality settings. (set) sets the default download directory for
			   NPR Fresh Air and NPR Wait Wait episodes.
       show                Just show the NPR core functionality settings.
       set                 Set the default download directories for NPR Fresh Air and NPR Wait Wait episodes.

   optional arguments:
     -h, --help            show this help message and exit
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for. Default is NONE.

You can show the core functionality settings by running ``nprconfig show``. In my case it shows this. I have blocked out my NPR API key.

.. code-block:: console

   NPR CONFIGURATION
   ----------------------  -------------------------------------
   NPR API KEY             XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   NPR Fresh Air download  /mnt/media/freshair
   NPR Wait Wait download  /mnt/media/waitwait
   ----------------------  -------------------------------------

Here is the help when running ``nprconfig set -h``,

.. code-block:: console

   usage: nprconfig set [-h] [--freshair FRESHAIR] [--waitwait WAITWAIT] [--api API]

   optional arguments:
     -h, --help           show this help message and exit
     --freshair FRESHAIR  Sets the default download directory for NPR Fresh Air episodes.
     --waitwait WAITWAIT  Sets the default download directory for NPR Wait Wait episodes.
     --api API            Sets the NPR API key.

.. _npr_freshair_label:
     
NPR Fresh Air
==============
These four executables handle `NPR Fresh Air`_ downloads: :ref:`freshair_label`, :ref:`freshair_crontab_label`, :ref:`freshair_fix_crontab_label`, and :ref:`freshair_by_year_label`.

.. _freshair_label:

``freshair``
---------------
``freshair`` is the main executable that downloads `NPR Fresh Air`_ episodes, converts them to M4A_ format, and then applies correct metadata. The help screen for this command line tool is here,


.. code-block::  console

   usage: freshair [-h] [--dirname DIRNAME] [--date DATE] [--mp3exist] [--debug] [--level {DEBUG,ERROR,INFO,NONE}]

   optional arguments:
     -h, --help            show this help message and exit
     --dirname DIRNAME     Name of the directory to store the file. Default is /mnt/media/freshair.
     --date DATE           The date, in the form of "January 1, 2014." The default is today's date, August 18, 2020.
     --mp3exist            If chosen, then do not download the transitional mp3 files. Use the ones that already exist.
     --debug               If chosen, run freshair in debug mode. Useful for debugging :)
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of
			   ['DEBUG', 'ERROR', 'INFO', 'NONE']. Default is NONE.

.. _freshair_crontab_label:
			   
``freshair_crontab``
----------------------
``freshair_crontab`` downloads an `NPR Fresh Air`_ episode on a given weekday. It should be called by a cron job or a systemd service that runs every weekday.

.. _freshair_fix_crontab_label:

``freshair_fix_crontab``
--------------------------
``freshair_fix_crontab`` tries to re-download `NPR Fresh Air`_ episodes that may be incomplete – defined as shorter than 30 minutes – and which are 90 days or older. This executable searches through the library of all NPR Fresh Air episodes, and tries to re-download older, possibly incomplete episodes.


.. _freshair_by_year_label:

``freshair_by_year``
---------------------
``freshair_by_year`` downloads all the NPR Fresh Air episodes in a given year. The help screen for this command line tool is here,

.. code-block:: console

   usage: freshair_by_year [-h] [--year YEAR] [--inputdir INPUTDIR] [--quiet] [--coverage] [--audit] [--level {DEBUG,ERROR,INFO,NONE}]

   optional arguments:
     -h, --help            show this help message and exit
     --year YEAR           Year in which to write out all Fresh Air episodes. Default is 2020.
     --inputdir INPUTDIR   Directory into which to store the NPR Fresh Air episodes. Default is /mnt/media/freshair.
     --quiet               If chosen, do not print verbose output from the action of this script. By default this is false.
     --coverage            If chosen, just give the list of missing Fresh Air episodes and nothing else.
     --audit               If chosen, do the audit picture here.
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of
			   ['DEBUG', 'ERROR', 'INFO', 'NONE']. Default is NONE.

.. _npr_waitwait_label:
			   
NPR Wait Wait
==============
These three executables handle `NPR Wait Wait <waitwait_>`_ downloads: :ref:`waitwait_label`, :ref:`waitwait_crontab_label`, and :ref:`waitwait_by_year_label`.

.. _waitwait_label:

``waitwait``
--------------
``waitwait`` is the main executable that downloads NPR Wait Wait episodes, converts them to M4A_ format, and then applies correct metadata. :py:mod:`waitwait_realmedia <nprstuff.core.waitwait_realmedia>` is a Python module that allows one to download `NPR Wait Wait <waitwait_>`_ episodes older than 2004, which are in RealMedia_ format. The help screen for this command line tool is here,

.. code-block:: console

   usage: waitwait [-h] [--dirname DIRNAME] [--date DATE] [--dump] [--level {DEBUG,ERROR,INFO,NONE}] [--justfix]

   optional arguments:
     -h, --help            show this help message and exit
     --dirname DIRNAME     Name of the directory to store the file. Default is /mnt/media/waitwait.
     --date DATE           The date, in the form of "January 1, 2014." The default is last Saturday, August 15, 2020.
     --dump                If chosen, download the NPR XML data sheet for this Wait Wait episode.
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for downloading NPR Wait Wait episodes or their XML representation of episode info. Can be one of
			   ['DEBUG', 'ERROR', 'INFO', 'NONE']. Default is NONE.
     --justfix             If chosen, just fix the title of an existing NPR Wait Wait episode's file.

.. _waitwait_crontab_label:
     
``waitwait_crontab``
---------------------
``waitwait_crontab`` downloads an NPR Wait Wait episode on a given Saturday. It should be called by a cron job or systemd service that is run every Saturday.

.. _waitwait_by_year_label:

``waitwait_by_year``
----------------------
``waitwait_by_year`` downloads all the NPR Wait Wait episodes in a given year. The help screen for this command line tool is here,

.. code-block:: console

   usage: waitwait_by_year [-h] [--year YEAR] [--inputdir INPUTDIR] [--quiet] [--level {DEBUG,ERROR,INFO,NONE}]

   optional arguments:
     -h, --help            show this help message and exit
     --year YEAR           Year in which to write out all Fresh Air episodes. Default is 2010.
     --inputdir INPUTDIR   Directory into which to store the NPR Wait Wait episodes. Default is /mnt/media/waitwait.
     --quiet               If chosen, do not print verbose output from the action of this script. By default this is false.
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for downloading NPR Wait Wait episodes or their XML representation of episode info. Can be one of
			   ['DEBUG', 'ERROR', 'INFO', 'NONE']. Default is NONE.

.. _this_american_life_label:
			   
This American Life
===================
The executable ``thisamericanlife`` *manually* downloads a given episode number of `This American Life`_. The help screen for this command line tool is here,

.. code-block:: console

   usage: thisamericanlife [-h] [--episode EPISODE] [--directory DIRECTORY] [--extra EXTRASTUFF] [--noverify] [--dump] [--level {DEBUG,ERROR,INFO,NONE}]

   optional arguments:
     -h, --help            show this help message and exit
     --episode EPISODE     Episode number of This American Life to download. Default is 150.
     --directory DIRECTORY
			   Directory into which to download This American Life episodes. Default is /mnt/media/thisamericanlife.
     --extra EXTRASTUFF    If defined, some extra stuff in the URL to get a This American Life episode.
     --noverify            If chosen, then do not verify the SSL connection.
     --dump                If chosen, just download the TAL episode XML into a file into the specified directory.
     --level {DEBUG,ERROR,INFO,NONE}
			   choose the debug level for downloading NPR Fresh Air episodes or their XML representation of episode info. Can be one of
			   ['DEBUG', 'ERROR', 'INFO', 'NONE']. Default is NONE.
