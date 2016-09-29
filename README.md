---

[![Join the chat at https://gitter.im/nprstuff-tanimislam/Lobby](https://badges.gitter.im/nprstuff-tanimislam/Lobby.svg)](https://gitter.im/nprstuff-tanimislam/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
author:
- Tanim Islam
title: nprstuff
...

I like NPR, so I made some scripts to download my favorite programs from
NPR. For now, I have something that downloads [Fresh
Air](http://www.npr.org/programs/fresh-air/), [Wait Wait..Don’t Tell
Me](http://www.npr.org/programs/wait-wait-dont-tell-me/), and [This
American Life](http://www.thisamericanlife.org/). This package can
probably, straightforwardly be extended to other NPR and PRI programs.

Although this project started off as a way to download these three
programs, I have expanded it to include a grab bag of altogether
different types of functionalities. What remains the same? This
distribution consists mainly of executable python scripts.

I organize this document into the following sections: , , (in folders
<span>`gui`</span> and <span>`gui2`</span>), and a small section called
.

This document was converted from a LaTeXsource using
[Pandoc](http://pandoc.org/index.html), via

    pandoc -s README.tex -o README.md

Core Functionality
==================

This consists of functionality to grab episodes from [Fresh
Air](http://www.npr.org/programs/fresh-air/), [Wait Wait..Don’t Tell
Me](http://www.npr.org/programs/wait-wait-dont-tell-me/), and [This
American Life](http://www.thisamericanlife.org/). These consist of the
following pieces of python code:

-   <span>`npr_utils.py`</span> contains common utilities to get the
    proper metadata for NPR programs, to name these media files in the
    proper date format, and to get the full paths to the
    [LibAV/FFMPEG](https://libav.org) and
    [HandBrakeCLI](https://handbrake.fr/) tools to create the NPR
    programs in m4a and mp3 formats (among other functionalities).

-   These four files handle NPR Fresh Air downloads:
    <span>`freshair.py`</span>, <span>`freshair_crontab.py`</span>,
    <span>`freshair_fix_crontab.py`</span>, and
    <span>`freshair_by_year.py`</span>.

    -   <span>`freshair.py`</span> is the main executable that downloads
        NPR Fresh Air episodes, converts them to m4a format, and then
        applies correct metadata. The help screen for this command line
        tool is here,

            Usage: freshair.py [options]

            Options:
              -h, --help         show this help message and exit
              --dirname=DIRNAME  Name of the directory to store the file. Default is
                                 /mnt/media/freshair.
              --date=DATE        The date, in the form of "January 1, 2014." The default
                                 is today's date, November 14, 2015.
              --debug            If chosen, run freshair.py in debug mode. Useful for
                                 debugging :)

    -   <span>`freshair_crontab.py`</span> downloads an NPR Fresh Air
        episode on a given weekday. It should be called by a cron job
        that should be run every weekday.

    -   <span>`freshair_fix_crontab.py`</span> tries to re-download NPR
        Fresh Air episodes that may be incomplete – defined as shorter
        than 30 minutes – and which are 90 days or older. This
        executable searches through the library of all NPR Fresh Air
        episodes, and tries to re-download older, possibly
        incomplete episodes.

    -   <span>`freshair_by_year.py`</span> downloads all the NPR Fresh
        Air episodes in a given year.

-   These four files handle NPR Wait Wait downloads:
    <span>`waitwait.py`</span>, <span>`waitwait_realmedia.py`</span>,
    <span>`waitwait_crontab.py`</span>, and
    <span>`waitwait_by_year.py`</span>.

    -   <span>`freshair.py`</span> is the main executable that downloads
        NPR Wait Wait episodes, converts them to m4a format, and then
        applies correct metadata. <span>`waitwait_realmedia.py`</span>
        is a python module that allows one to download NPR Wait Wait
        episodes older than 2004, which are in
        [RealMedia](https://en.wikipedia.org/wiki/RealMedia) format. The
        help screen for this command line tool is here,

            Usage: waitwait.py [options]

            Options:
              -h, --help         show this help message and exit
              --dirname=DIRNAME  Name of the directory to store the file. Default is
                                 /mnt/media/waitwait.
              --date=DATE        The date, in the form of "January 1, 2014." The default
                                 is last Saturday, November 14, 2015.
              --debugonly        If chosen, download the NPR XML data sheet for this Wait
                                 Wait episode.

    -   <span>`waitwait_crontab.py`</span> downloads an NPR Wait Wait
        episode on a given Saturday. It should be called by a cron job
        that should be run every Saturday.

    -   <span>`waitwait_by_year.py`</span> downloads all the NPR Wait
        Wait episodes in a given year.

-   <span>`thisamericanlife.py`</span> *manually* downloads a given
    episode number of This American Life. This executable uses a custom
    online archive for older This American Life episodes that are
    described
    [here](http://www.dirtygreek.org/t/download-this-american-life-episodes).
    The help screen for this command line tool is here,

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

-   <span>`autoCropImage.py`</span> automatically crops image (png,
    jpeg, tiff, etc.) files to remove whitespace. The default whitespace
    color is <span>`white`</span>. The help screen for this command line
    tool is here,

        Usage: autoCropImage.py [options]

        Options:
          -h, --help       show this help message and exit
          --input=INPUT    Name of the input file.
          --output=OUTPUT  Name of the output file. Optional.
          --color=COLOR    Name of the color over which to autocrop. Default is white.

-   <span>`convertImage.py`</span> uses the [CloudConvert REST
    API](https://cloudconvert.com/apiconsole) to *smoothly and without
    pain points* convert and resize SVG images to PNG images of the same
    base name. The help screen for this command line tool is here,

        Usage: convertImage.py [options]

        Options:
          -h, --help           show this help message and exit
          --filename=FILENAME  Name of the input SVG file.
          --width=WIDTH        If defined, new width of the file. Optional

-   <span>`changedates.py`</span> changes the creation date of JPG and
    MOV files, that my Canon digital camera creates, by up and down
    one year. I created this tool because my Canon digital camera does
    not set the right year on the creation date for image files
    it creates. This caused problems when I uploaded those images to
    [Google Picasa](https://picasaweb.google.com/home) or
    [Google+](https://plus.google.com/). The help screen for this
    command line tool is here,

        Usage: changedates.py [options]

        Options:
          -h, --help         show this help message and exit
          --dirname=DIRNAME  Name of the directory to look for jpeg files.
          --movs             If chosen, process MOV files instead.
          --minus            If chosen, subtract a year from the files.

-   <span>`music_to_m4a.py`</span> can convert a single file from
    mp3/ogg/flac format to m4a format while preserving music file
    metadata, and can optionally set the total number of album tracks
    and the album cover if the music files is in an album. It can also
    rename an m4a music file into the format “*artist name* - *song
    name*.m4a.” The help screen for this command line tool is here,

        Usage: music_to_m4a.py [options]

        Options:
          -h, --help            show this help message and exit
          --inputfile=INPUTFILE
                                Name of the input audio file to convert.
          --outfile=OUTFILE     Optional name of the output file.
          --tottracks=TOTTRACKS
                                Optional total number of tracks in album of which song
                                is a part.
          --albumloc=ALBUMLOC   Optional path to location of the album cover image
                                file. Must be in JPEG or PNG.
          --quiet               If chosen, then verbosely print output of processing.
          --rename              If chosen, simply rename the m4a file to the form
                                <artist>.<song title>.m4a

-   <span>`download_surahs.py`</span> downloads recorded surahs
    ([Abdur-Rashid Sufi](http://quranicaudio.com/quran/109)) to a
    directory of your choice. The help screen for this command line tool
    is here,

        Usage: download_surahs.py [options]

        Options:
          -h, --help       show this help message and exit
          --outdir=OUTDIR  Directory to put this data into. Default is
                           /mnt/software/sources/pythonics/nprstuff.

Graphics Functionality
======================

This section describes the two graphical tools I have developed:
<span>`gui`</span> matches a small subset of functionality that the
[Readability](https://www.readability.com) tool handles excellently;
<span>`gui2`</span> is a
[PyQt4](https://www.riverbankcomputing.com/software/pyqt/download) GUI
front-end to the [Readability](https://www.readability.com) API.

GUI: Media Website Text Formatter
---------------------------------

This GUI can read from the following media websites: [Lightspeed
Magazine](http://www.lightspeedmagazine.com/),
[Medium](https://medium.com/), [The New
Yorker](http://www.newyorker.com/), [The New York
Times](http://www.nytimes.com/?WT.z_jog=1), and the [Virginia Quarterly
Review](http://www.vqronline.org/). Here is a screenshot!

\[!ht\]<span>0.65</span> ![A screenshot of the GUI reader, converting
the URL for the [The New York Times](http://www.nytimes.com) into text.
Note the separate icons above for the five media websites from which
this GUI can read.<span
data-label="fig:gui_screenshot"></span>](images/gui_screenshot.png "fig:"){width="\linewidth"}

\[!ht\]<span>0.34</span>

The screenshots of the save file dialog and the print preview dialog are
shown Fig. \[fig:gui\_screenshot\_save\] and
Fig. \[fig:gui\_screenshot\_printpreview\], respectively.

\[!ht\]<span>0.4</span> ![The GUI screenshot of the print preview
dialog.<span
data-label="fig:gui_screenshot_printpreview"></span>](images/gui_screenshot_save.png "fig:"){width="\linewidth"}

\[!ht\]<span>0.5</span> ![The GUI screenshot of the print preview
dialog.<span
data-label="fig:gui_screenshot_printpreview"></span>](images/gui_screenshot_printpreview.png "fig:"){width="\linewidth"}

Note, here I do not support or maintain this tool after I found out
about [Readability](https://www.readability.com).

GUI2: Readability GUI Front-End
-------------------------------

This is the PyQt4 GUI front-end to
[Readability](https://www.readability.com). A screenshot of the list of
articles widget is shown in
Fig. (\[fig:gui2\_screenshot\_articlelist\]), and a screenshot of the
article text widget is shown in
Fig. (\[fig:gui2\_screenshot\_articletext\]).

\[!ht\]<span>0.52</span> ![The text form of the article’s content, with
working dialogs for `Font` and `Print Preview`.<span
data-label="fig:gui2_screenshot_articletext"></span>](images/gui2_screenshot_articlelist.png "fig:"){width="\linewidth"}

\[!ht\]<span>0.45</span> ![The text form of the article’s content, with
working dialogs for `Font` and `Print Preview`.<span
data-label="fig:gui2_screenshot_articletext"></span>](images/gui2_screenshot_articletext.png "fig:"){width="\linewidth"}

A screenshot of the font changing dialog, the <span>`Font`</span>
button, is shown in Fig. (\[fig:gui2\_screenshot\_fontdialog\]). A
screenshot of the print preview dialog, the <span>`Print`</span> button,
is shown in Fig. (\[fig:gui2\_screenshot\_printpreviewdialog\]).

\[!ht\]<span>0.53</span> ![The print preview dialog launched by the
`Print` button in the article text widget.<span
data-label="fig:gui2_screenshot_printpreviewdialog"></span>](images/gui2_screenshot_fontdialog.png "fig:"){width="\linewidth"}

\[!ht\]<span>0.45</span> ![The print preview dialog launched by the
`Print` button in the article text widget.<span
data-label="fig:gui2_screenshot_printpreviewdialog"></span>](images/gui2_screenshot_printpreviewdialog.png "fig:"){width="\linewidth"}

In the immediate future, I plan on at least implementing the following,
all using the Readability API.

-   <span>`EPUB`</span> button, to create the article in
    [EPUB](https://en.wikipedia.org/wiki/EPUB) format.

-   Adding and deleting articles through the article list widget.

Oldstuff
========

These are tools that I do not maintain, located in the
<span>`oldstuff`</span> folder, but which others may find useful. These
are pieces of code that I have started, but which are unmaintained.
These are the following pieces of code: <span>`freshair.sh`</span>,
<span>`waitwait.sh`</span>, and <span>`google_pull_contacts.py`</span>.
