.. include:: urls.rst

================================================
Email APIs
================================================
This document describes the nprstuff email API, which provides the lower-level back-end functionality for ``rest_email``. These modules live in ``nprstuff.npremail``.

The main module implements a *bunch* of different things

* validating and converting reStructuredText_ strings to rich HTML.

* doing stuff with Imgur_ credentials.

* doing stuff with Google OAuth2 authentication to services that will send email, and get google contacts, using Google's APIs.

* A single convenience widget, :py:class:`HtmlView <nprstuff.npremail.HtmlView>`, that acts as a rudimentary browser that can display rich HTML.

.. automodule:: nprstuff.npremail
   :members:

email module
---------------
This module contains common utilities to retrieve contacts, craft email, and send email. This module lives in ``nprstuff.npremail.npremail``.

.. automodule:: nprstuff.npremail.npremail
   :members:

email_imgur module
-------------------
This module hooks into the Imgur_ account, and the albums and images in albums, that it contains. It also implements widgets in ``rest_email`` that manipulate the images in one's Imgur_ album. This module lives in ``nprstuff.npremail.email_imgur``.

.. automodule:: nprstuff.npremail.email_imgur
   :members:
