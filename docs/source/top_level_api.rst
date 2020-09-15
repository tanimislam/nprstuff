.. include:: urls.rst

Top Level API
================================================
This document describes the lower level NPRStuff API, upon which all the command line and GUI tools are based. It lives in ``nprstuff``.

This module implements the lower-level functionality that does or has the following:

* access and retrieve configuration and other data from an SQLite3_ database using SQLAlchemy_ object relational mapping (ORM) classes. The SQLite3_ database is stored in ``~/.config/nprstuff/app.db``.

* :py:class:`NPRStuffConfig <nprstuff.NPRStuffConfig>` is an ORM class that stores configuration information.

* :py:meth:`create_all <nprstuff.create_all>` instantiates necessary SQLite3_ tables in the configuration table if they don't already exist.

* low level PyQt5_ derived widgets used for the other GUIs in NPRStuff: :py:class:`ProgressDialog <nprstuff.ProgressDialog>`, :py:class:`QDialogWithPrinting <nprstuff.QDialogWithPrinting>`, and :py:class:`QLabelWithSave <nprstuff.QLabelWithSave>`.

.. automodule:: nprstuff
   :members:
