.. raw:: latex

   \documentclass[]{article}
   \usepackage{lmodern}
   \usepackage{amssymb,amsmath}
   \usepackage{ifxetex,ifluatex}
   \usepackage{fixltx2e} % provides \textsubscript
   \ifnum 0\ifxetex 1\fi\ifluatex 1\fi=0 % if pdftex
     \usepackage[T1]{fontenc}
     \usepackage[utf8]{inputenc}
   \else % if luatex or xelatex
     \ifxetex
       \usepackage{mathspec}
     \else
       \usepackage{fontspec}
     \fi
     \defaultfontfeatures{Mapping=tex-text,Scale=MatchLowercase}
     \newcommand{\euro}{€}
   \fi
   % use upquote if available, for straight quotes in verbatim environments
   \IfFileExists{upquote.sty}{\usepackage{upquote}}{}
   % use microtype if available
   \IfFileExists{microtype.sty}{%
   \usepackage{microtype}
   \UseMicrotypeSet[protrusion]{basicmath} % disable protrusion for tt fonts
   }{}
   \makeatletter
   \@ifpackageloaded{hyperref}{}{%
   \ifxetex
     \usepackage[setpagesize=false, % page size defined by xetex
                 unicode=false, % unicode breaks when used with xetex
                 xetex]{hyperref}
   \else
     \usepackage[unicode=true]{hyperref}
   \fi
   }
   \@ifpackageloaded{color}{
       \PassOptionsToPackage{usenames,dvipsnames}{color}
   }{%
       \usepackage[usenames,dvipsnames]{color}
   }
   \makeatother
   \hypersetup{breaklinks=true,
               bookmarks=true,
               pdfauthor={Tanim Islam},
               pdftitle={nprstuff},
               colorlinks=true,
               citecolor=blue,
               urlcolor=blue,
               linkcolor=magenta,
               pdfborder={0 0 0}
               }
   \urlstyle{same}  % don't use monospace font for urls
   \usepackage{graphicx,grffile}
   \makeatletter
   \def\maxwidth{\ifdim\Gin@nat@width>\linewidth\linewidth\else\Gin@nat@width\fi}
   \def\maxheight{\ifdim\Gin@nat@height>\textheight\textheight\else\Gin@nat@height\fi}
   \makeatother
   % Scale images if necessary, so that they will not overflow the page
   % margins by default, and it is still possible to overwrite the defaults
   % using explicit options in \includegraphics[width, height, ...]{}
   \setkeys{Gin}{width=\maxwidth,height=\maxheight,keepaspectratio}
   \setlength{\parindent}{0pt}
   \setlength{\parskip}{6pt plus 2pt minus 1pt}
   \setlength{\emergencystretch}{3em}  % prevent overfull lines
   \providecommand{\tightlist}{%
     \setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
   \setcounter{secnumdepth}{0}

   \title{nprstuff}
   \author{Tanim Islam}
   \date{}

   % Redefines (sub)paragraphs to behave more like sections
   \ifx\paragraph\undefined\else
   \let\oldparagraph\paragraph
   \renewcommand{\paragraph}[1]{\oldparagraph{#1}\mbox{}}
   \fi
   \ifx\subparagraph\undefined\else
   \let\oldsubparagraph\subparagraph
   \renewcommand{\subparagraph}[1]{\oldsubparagraph{#1}\mbox{}}
   \fi

.. raw:: latex

   \begin{document}
   \maketitle

   I like NPR, so I made some scripts to download my favorite programs from
   NPR. For now, I have something that downloads
   \href{http://www.npr.org/programs/fresh-air/}{Fresh Air},
   \href{http://www.npr.org/programs/wait-wait-dont-tell-me/}{Wait
   Wait..Don't Tell Me}, and \href{http://www.thisamericanlife.org/}{This
   American Life}. This package can probably, straightforwardly be extended
   to other NPR and PRI programs.

   Although this project started off as a way to download these three
   programs, I have expanded it to include a grab bag of altogether
   different types of functionalities. What remains the same? This
   distribution consists mainly of executable python scripts.

   I organize this document into the following sections: Core
   Functionality, New Functionality, Graphics Functionality (in folders
   {\texttt{gui}} and {\texttt{gui2}}), and a small section called
   Oldstuff.

   This document was converted from a LaTeXsource using
   \href{http://pandoc.org/index.html}{Pandoc}, via

   \begin{verbatim}
   pandoc -s README.tex -o README.rst
   \end{verbatim}

   \section{Core Functionality}\label{sec:coreux5ffunctionality}

   This consists of functionality to grab episodes from
   \href{http://www.npr.org/programs/fresh-air/}{Fresh Air},
   \href{http://www.npr.org/programs/wait-wait-dont-tell-me/}{Wait
   Wait..Don't Tell Me}, and \href{http://www.thisamericanlife.org/}{This
   American Life}. These consist of the following pieces of python code:

   \begin{itemize}
   \item
     {\texttt{npr\_utils.py}} contains common utilities to get the proper
     metadata for NPR programs, to name these media files in the proper
     date format, and to get the full paths to the
     \href{https://libav.org}{LibAV/FFMPEG} and
     \href{https://handbrake.fr/}{HandBrakeCLI} tools to create the NPR
     programs in m4a and mp3 formats (among other functionalities).
   \item
     These four files handle NPR Fresh Air downloads:
     {\texttt{freshair.py}}, {\texttt{freshair\_crontab.py}},
     {\texttt{freshair\_fix\_crontab.py}}, and
     {\texttt{freshair\_by\_year.py}}.

     \begin{itemize}
     \item
       {\texttt{freshair.py}} is the main executable that downloads NPR
       Fresh Air episodes, converts them to m4a format, and then applies
       correct metadata. The help screen for this command line tool is
       here,

   \begin{verbatim}
   Usage: freshair.py [options]

   Options:
     -h, --help         show this help message and exit
     --dirname=DIRNAME  Name of the directory to store the file. Default is
                        /mnt/media/freshair.
     --date=DATE        The date, in the form of "January 1, 2014." The default
                        is today's date, November 14, 2015.
     --debug            If chosen, run freshair.py in debug mode. Useful for
                        debugging :)
   \end{verbatim}
     \item
       {\texttt{freshair\_crontab.py}} downloads an NPR Fresh Air episode
       on a given weekday. It should be called by a cron job that should be
       run every weekday.
     \item
       {\texttt{freshair\_fix\_crontab.py}} tries to re-download NPR Fresh
       Air episodes that may be incomplete -- defined as shorter than 30
       minutes -- and which are 90 days or older. This executable searches
       through the library of all NPR Fresh Air episodes, and tries to
       re-download older, possibly incomplete episodes.
     \item
       {\texttt{freshair\_by\_year.py}} downloads all the NPR Fresh Air
       episodes in a given year.
     \end{itemize}
   \item
     These four files handle NPR Wait Wait downloads:
     {\texttt{waitwait.py}}, {\texttt{waitwait\_realmedia.py}},
     {\texttt{waitwait\_crontab.py}}, and {\texttt{waitwait\_by\_year.py}}.

     \begin{itemize}
     \item
       {\texttt{freshair.py}} is the main executable that downloads NPR
       Wait Wait episodes, converts them to m4a format, and then applies
       correct metadata. {\texttt{waitwait\_realmedia.py}} is a python
       module that allows one to download NPR Wait Wait episodes older than
       2004, which are in
       \href{https://en.wikipedia.org/wiki/RealMedia}{RealMedia} format.
       The help screen for this command line tool is here,

   \begin{verbatim}
   Usage: waitwait.py [options]

   Options:
     -h, --help         show this help message and exit
     --dirname=DIRNAME  Name of the directory to store the file. Default is
                        /mnt/media/waitwait.
     --date=DATE        The date, in the form of "January 1, 2014." The default
                        is last Saturday, November 14, 2015.
     --debugonly        If chosen, download the NPR XML data sheet for this Wait
                        Wait episode.
   \end{verbatim}
     \item
       {\texttt{waitwait\_crontab.py}} downloads an NPR Wait Wait episode
       on a given Saturday. It should be called by a cron job that should
       be run every Saturday.
     \item
       {\texttt{waitwait\_by\_year.py}} downloads all the NPR Wait Wait
       episodes in a given year.
     \end{itemize}
   \item
     {\texttt{thisamericanlife.py}} \emph{manually} downloads a given
     episode number of This American Life. This executable uses a custom
     online archive for older This American Life episodes that are
     described
     \href{http://www.dirtygreek.org/t/download-this-american-life-episodes}{here}.
     The help screen for this command line tool is here,

   \begin{verbatim}
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
   \end{verbatim}
   \end{itemize}

   \section{New Functionality}\label{sec:newux5ffunctionality}

   This consists of newer functionality that does not download NPR
   episodes, nor can one straightforwardly modify them to download NPR
   episodes. These consist of the following pieces of python code.

   \begin{itemize}
   \item
     {\texttt{autoCropImage.py}} automatically crops image (png, jpeg,
     tiff, etc.) files to remove whitespace. The default whitespace color
     is {\texttt{white}}. The help screen for this command line tool is
     here,

   \begin{verbatim}
   Usage: autoCropImage.py [options]

   Options:
     -h, --help       show this help message and exit
     --input=INPUT    Name of the input file.
     --output=OUTPUT  Name of the output file. Optional.
     --color=COLOR    Name of the color over which to autocrop. Default is white.
   \end{verbatim}
   \item
     {\texttt{convertImage.py}} uses the
     \href{https://cloudconvert.com/apiconsole}{CloudConvert REST API} to
     \emph{smoothly and without pain points} convert and resize SVG images
     to PNG images of the same base name. The help screen for this command
     line tool is here,

   \begin{verbatim}
   Usage: convertImage.py [options]

   Options:
     -h, --help           show this help message and exit
     --filename=FILENAME  Name of the input SVG file.
     --width=WIDTH        If defined, new width of the file. Optional
   \end{verbatim}
   \item
     {\texttt{changedates.py}} changes the creation date of JPG and MOV
     files, that my Canon digital camera creates, by up and down one year.
     I created this tool because my Canon digital camera does not set the
     right year on the creation date for image files it creates. This
     caused problems when I uploaded those images to
     \href{https://picasaweb.google.com/home}{Google Picasa} or
     \href{https://plus.google.com/}{Google+}. The help screen for this
     command line tool is here,

   \begin{verbatim}
   Usage: changedates.py [options]

   Options:
     -h, --help         show this help message and exit
     --dirname=DIRNAME  Name of the directory to look for jpeg files.
     --movs             If chosen, process MOV files instead.
     --minus            If chosen, subtract a year from the files.
   \end{verbatim}
   \item
     {\texttt{music\_to\_m4a.py}} can convert a single file from
     mp3/ogg/flac format to m4a format while preserving music file
     metadata, and can optionally set the total number of album tracks and
     the album cover if the music files is in an album. It can also rename
     an m4a music file into the format ``\emph{artist name} - \emph{song
     name}.m4a.'' The help screen for this command line tool is here,

   \begin{verbatim}
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
   \end{verbatim}
   \item
     {\texttt{download\_surahs.py}} downloads recorded surahs
     (\href{http://quranicaudio.com/quran/109}{Abdur-Rashid Sufi}) to a
     directory of your choice. The help screen for this command line tool
     is here,

   \begin{verbatim}
   Usage: download_surahs.py [options]

   Options:
     -h, --help       show this help message and exit
     --outdir=OUTDIR  Directory to put this data into. Default is
                      /mnt/software/sources/pythonics/nprstuff.
   \end{verbatim}
   \end{itemize}

   \section{Graphics Functionality}\label{sec:graphicsux5ffunctionality}

   This section describes the two graphical tools I have developed:
   {\texttt{gui}} matches a small subset of functionality that the
   \href{https://www.readability.com}{Readability} tool handles
   excellently; {\texttt{gui2}} is a
   \href{https://www.riverbankcomputing.com/software/pyqt/download}{PyQt4}
   GUI front-end to the \href{https://www.readability.com}{Readability}
   API.

   \subsection{GUI: Media Website Text Formatter}\label{subsec:gui}

   This GUI can read from the following media websites:
   \href{http://www.lightspeedmagazine.com/}{Lightspeed Magazine},
   \href{https://medium.com/}{Medium}, \href{http://www.newyorker.com/}{The
   New Yorker}, \href{http://www.nytimes.com/?WT.z_jog=1}{The New York
   Times}, and the \href{http://www.vqronline.org/}{Virginia Quarterly
   Review}. Here is a screenshot!

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui_screenshot.png}
   \caption{A screenshot of the GUI reader, converting the URL for the
   \href{http://www.nytimes.com}{The New York Times} into text. Note the
   separate icons above for the five media websites from which this GUI can
   read.{}}
   \end{figure}

   The screenshots of the save file dialog and the print preview dialog are
   shown Fig.~{[}fig:gui\_screenshot\_save{]} and
   Fig.~{[}fig:gui\_screenshot\_printpreview{]}, respectively.

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui_screenshot_save.png}
   \caption{The GUI screenshot of the print preview dialog.{}}
   \end{figure}

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui_screenshot_printpreview.png}
   \caption{The GUI screenshot of the print preview dialog.{}}
   \end{figure}

   Note, here I do not support or maintain this tool after I found out
   about \href{https://www.readability.com}{Readability}.

   \subsection{GUI2: Readability GUI Front-End}\label{subsec:gui2}

   This is the PyQt4 GUI front-end to
   \href{https://www.readability.com}{Readability}. A screenshot of the
   list of articles widget is shown in
   Fig.~({[}fig:gui2\_screenshot\_articlelist{]}), and a screenshot of the
   article text widget is shown in
   Fig.~({[}fig:gui2\_screenshot\_articletext{]}).

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui2_screenshot_articlelist.png}
   \caption{The text form of the article's content, with working dialogs
   for \texttt{Font} and \texttt{Print\ Preview}.{}}
   \end{figure}

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui2_screenshot_articletext.png}
   \caption{The text form of the article's content, with working dialogs
   for \texttt{Font} and \texttt{Print\ Preview}.{}}
   \end{figure}

   A screenshot of the font changing dialog, the {\texttt{Font}} button, is
   shown in Fig.~({[}fig:gui2\_screenshot\_fontdialog{]}). A screenshot of
   the print preview dialog, the {\texttt{Print}} button, is shown in
   Fig.~({[}fig:gui2\_screenshot\_printpreviewdialog{]}).

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui2_screenshot_fontdialog.png}
   \caption{The print preview dialog launched by the \texttt{Print} button
   in the article text widget.{}}
   \end{figure}

   \begin{figure}[htbp]
   \centering
   \includegraphics{images/gui2_screenshot_printpreviewdialog.png}
   \caption{The print preview dialog launched by the \texttt{Print} button
   in the article text widget.{}}
   \end{figure}

   In the immediate future, I plan on at least implementing the following,
   all using the Readability API.

   \begin{itemize}
   \item
     {\texttt{EPUB}} button, to create the article in
     \href{https://en.wikipedia.org/wiki/EPUB}{EPUB} format.
   \item
     Adding and deleting articles through the article list widget.
   \end{itemize}

   \section{Oldstuff}\label{sec:oldstuff}

   These are tools that I do not maintain, located in the
   {\texttt{oldstuff}} folder, but which others may find useful. These are
   pieces of code that I have started, but which are unmaintained. These
   are the following pieces of code: {\texttt{freshair.sh}},
   {\texttt{waitwait.sh}}, and {\texttt{google\_pull\_contacts.py}}.

   \end{document}


