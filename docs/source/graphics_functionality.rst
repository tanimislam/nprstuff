.. include:: urls.rst

Graphics Functionality
^^^^^^^^^^^^^^^^^^^^^^^^

This section describes the two graphical tools I have developed: :numref:`gui_section_label` matches a small subset of functionality that the Readability_ tool handles excellently; :numref:`gui2_section_label` is a PyQt4_ GUI front-end to the Readability_ API.

.. _gui_section_label:

GUI: Media Website Text Formatter
------------------------------------

This GUI can read from the following media websites: `Lightspeed Magazine`_, Medium_, `The New Yorker`_, `The New York Times`_, and the `Virginia Quarterly Review`_. Here is a screenshot!

.. figure:: images/gui_screenshot.png
   :width: 100%
   :align: left

   A screenshot of the GUI reader, converting the URL for the `The New York Times`_ into text. Note the separate icons above for the five media websites from which this GUI can read.

The screenshots of the save file dialog and the print preview dialog are shown below.

.. figure:: images/gui_screenshot_save.png
   :width: 100%
   :align: left

   The GUI screenshot of the save dialog.

.. figure:: images/gui_screenshot_printpreview.png
   :width: 100%
   :align: left

   The GUI screenshot of the print preview dialog.

I do not support or maintain this tool after I found out about Readability_.

**Furthermore**, Readability is long gone and its developers and maintainers have scattered to the four winds. None of its functionalities work anymore.

.. _gui2_section_label:
   
GUI2: Readability GUI Front-End
----------------------------------

This is the PyQt4_ GUI front-end to Readability_.

.. figure:: images/gui2_screenshot_articlelist.png
   :width: 100%
   :align: left

   The list form of the article’s content, with working dialogs for ``Font`` and ``Print Preview``. Coloration helps with readability.

.. figure:: images/gui2_screenshot_articletext.png
   :width: 100%
   :align: left
	   
   The text form of the article’s content, with working dialogs for ``Font`` and ``Print Preview``. The behavior of the buttons are shown in the subsequent figures.

A screenshot of the font changing dialog, the ``Font`` button, and a screenshot of the print preview dialog, the ``Print`` button, are shown below.

.. figure:: images/gui2_screenshot_fontdialog.png
   :width: 100%
   :align: left

   The ``Font`` button dialog. This lets the user select through the fonts that currently exist in the system.

.. figure:: images/gui2_screenshot_printpreviewdialog.png
   :width: 100%
   :align: left
	   
   The print preview dialog launched by the ``Print`` button in the article text widget.

In the immediate future, I plan on at least implementing the following, all using the Readability_ API.

* ``EPUB`` button, to create the article in EPUB_ format.

* Adding and deleting articles through the article list widget.
