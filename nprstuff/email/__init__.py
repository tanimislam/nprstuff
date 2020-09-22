import oauth2client.client, json, requests, os, logging, hashlib
from functools import partial
from google.oauth2.credentials import Credentials
from docutils.examples import html_parts
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtNetwork import QNetworkAccessManager
#
from nprstuff import session, NPRStuffConfig, resourceDir

def md5sum( filename ):
    """
    Taken from `This StackOverflow`_ on how to calculate the MD5_ sum of a file.
    
    :param str filename: the candidate file's name to open.
    :returns: an MD5 hash of the file.
    :rtype: str

    .. _`This StackOverflow`: https://stackoverflow.com/a/7829658/3362358
    .. _MD5: https://en.wikipedia.org/wiki/MD5
    """
    assert( os.path.isfile( filename ) )
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
        return d.hexdigest()

def format_size( fsize_b ):
    """
    Formats the bytes value into a string with KiB, MiB or GiB units. This code has been copied from :py:meth:`deluge's format_size <deluge.ui.console.utils.format_utils.format_size>`.

    :param int fsize_b: the filesize in bytes.
    :returns: formatted string in KiB, MiB or GiB units.
    :rtype: str

    **Usage**
    
    >>> format_size( 112245 )
    '109.6 KiB'

    """
    fsize_kb = fsize_b / 1024.0
    if fsize_kb < 1024:
        return "%.1f KiB" % fsize_kb
    fsize_mb = fsize_kb / 1024.0
    if fsize_mb < 1024:
        return "%.1f MiB" % fsize_mb
    fsize_gb = fsize_mb / 1024.0
    return "%.1f GiB" % fsize_gb

def check_valid_RST( myString ):
    """
    Checks to see whether the input string is valid reStructuredText_.

    :param str myString: the candidate reStructuredText_ input.
    :returns: ``True`` if valid, otherwise ``False``.
    :rtype: bool

    .. seealso:: :py:meth:`convert_string_RST <nprstuff.email.convert_string_RST>`.

    .. _reStructuredText: https://en.wikipedia.org/wiki/ReStructuredText
    """
    body = html_parts( myString)[ 'body' ]
    html = BeautifulSoup( body, 'lxml' )
    error_messages = html.find_all('p', { 'class' : 'system-message-title' } )
    return len( error_messages) == 0

def convert_string_RST( myString ):
    """
    Converts a valid reStructuredText_ input string into rich HTML.

    :param str myString: the candidate reStructuredText_ input.
    :returns: If the input string is valid reStructuredText_, returns the rich HTML as a :py:class:`string <str>`. Otherwise emits a :py:meth:`logging error message <logging.error>` and returns ``None``.
    :rtype: str

    .. seealso:: :py:meth:`check_valid_RST <nprstuff.email.check_valid_RST>`.
    """
    if not check_valid_RST( myString ):
        logging.error( "Error, could not convert %s into RST." % myString )
        return None
    html_body = html_parts( myString )[ 'whole' ]
    html = BeautifulSoup( html_body, 'lxml' )
    return html.prettify( )


def get_imgurl_credentials( ):
    """
    retrieves the Imgur_ API credentials from the SQLite3_ configuration database.

    :returns: a :py:class:`dict` of the Imgur_ API credentials. Its structure is,

    .. code-block:: python
    
       { 'clientID': XXXX,
         'clientSECRET': XXXX,
         'clientREFRESHTOKEN': XXXX,
         'mainALBUMID': XXXX,
         'mainALBUMTITLE': XXXX }

    :rtype: dict

    .. seealso::

       * :py:meth:`check_imgurl_credentials <nprstuff.email.check_imgurl_credentials>`.
       * :py:meth:`store_imgurl_credentials <nprstuff.email.store_imgurl_credentials>`.
    
    .. _Imgur: https://imgur.com/
    .. _SQLite3: https://en.wikipedia.org/wiki/SQLite
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'imgurl' ).first( )
    if val is None:
        raise ValueError( "ERROR, COULD NOT FIND IMGUR CREDENTIALS." )
    data_imgurl = val.data
    return data_imgurl

def check_imgurl_credentials(
    clientID, clientSECRET, clientREFRESHTOKEN, verify = True ):
    """
    validate the Imgur_ API credentials with the provided API client ID, secret, and refresh token.

    :param str clientID: the Imgur_ client ID.
    :param str clientSECRET: the Imgur_ client secret.
    :param str clientREFRESHTOKEN: the Imgur_ client refresh token.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: whether the new credentials are correct.
    
    :rtype: bool

    .. seealso::

       * :py:meth:`get_imgurl_credentials <nprstuff.email.get_imgurl_credentials>`.
       * :py:meth:`store_imgurl_credentials <nprstuff.email.store_imgurl_credentials>`.
    """
    response = requests.post(
         'https://api.imgur.com/oauth2/token',
        data = {'client_id': clientID,
                'client_secret': clientSECRET,
                'grant_type': 'refresh_token',
                'refresh_token': clientREFRESHTOKEN },
        verify = verify )
    if response.status_code != 200:
        return False
    return True

def store_imgurl_credentials(
    clientID, clientSECRET, clientREFRESHTOKEN, verify = True,
    mainALBUMID = None, mainALBUMNAME = None ):
    """
    stores the Imgur_ API credentials into the SQLite3_ configuration database.

    :param str clientID: the Imgur_ client ID.
    :param str clientSECRET: the Imgur_ client secret.
    :param str clientREFRESHTOKEN: the Imgur_ client refresh token.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param str mainALBUMID: optional argument. If given, then store this album hash into the database.
    :param str mainALBUMNAME: optional argument. If given, then store this album hash into the database.
    
    :returns: the string ``"SUCCESS"`` if could store the new Imgur_ credentials. Otherwise, the string ``'ERROR, COULD NOT STORE IMGURL CREDENTIALS.'``.
    
    :rtype: str

    .. seealso::

       * :py:meth:`check_imgurl_credentials <nprstuff.email.check_imgurl_credentials>`.
       * :py:meth:`get_imgurl_credentials <nprstuff.email.get_imgurl_credentials>`.
    """
    isValid = check_imgurl_credentials(
        clientID, clientSECRET, clientREFRESHTOKEN, verify = verify )
    if not isValid: return 'ERROR, COULD NOT STORE IMGURL CREDENTIALS.'
    datum = {
        'clientID' : clientID,
        'clientSECRET' : clientSECRET,
        'clientREFRESHTOKEN' : clientREFRESHTOKEN
    }
    if mainALBUMID is not None:
        datum[ 'mainALBUMID' ] = mainALBUMID
    if mainALBUMNAME is not None:
        datum[ 'mainALBUMNAME' ] = mainALBUMNAME
    
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'imgurl' ).first( )
    if val is not None:
        session.delete( val )
        session.commit( )
    newval = NPRStuffConfig( service = 'imgurl', data = datum )
    session.add( newval )
    session.commit( )
    return 'SUCCESS'

def oauthGetOauth2ClientGoogleCredentials( ):
    """
    Gets the `Google Oauth2`_ credentials, stored in the SQLite3_ configuration database, in the form of a refreshed :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` object. This OAuth2 authentication method IS used for all the services accessed by NPRStuff_.

    :returns: a :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` form of the `Google Oauth2`_ credentials for various Oauth2 services.
    :rtype: :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>`
    
    .. seealso::

       * :py:meth:`oauthCheckGoogleCredentials <nprstuff.email.oauthCheckGoogleCredentials>`.
       * :py:meth:`oauth_generate_google_permission_url <nprstuff.email.oauth_generate_google_permission_url>`.
       * :py:meth:`oauth_store_google_credentials <nprstuff.email.oauth_store_google_credentials>`.

    .. _NPRStuff: https://nprstuff.readthedocs.io
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'google' ).first( )
    if val is None: return None
    cred_data = val.data
    credentials = oauth2client.client.OAuth2Credentials.from_json(
        json.dumps( cred_data ) )
    return credentials

def oauth_generate_google_permission_url( ):
    """
    Generates a `Google OAuth2`_ web-based flow for all the Google services used in NPRStuff_. The authentication process that uses this flow is described in :ref:`this subsection <Summary of Setting Up Google Credentials>`. Here are the programmatic steps to finally generate an :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` object.
    
      1. Get the :py:class:`OAuth2WebServerFlow <oauth2client.client.OAuth2WebServerFlow>` and authentication URI.

         .. code-block:: python

            flow, auth_uri = oauth_generate_google_permission_url( )

      2. Go to the URL, ``auth_uri``, in a browser, grant permissions, and copy the authorization code in the browser window. This authorization code is referred to as ``authorization_code``.

      3. Create the :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` using ``authorization_code``.
    
         .. code-block:: python

            credentials = flow.step2_exchange( authorization_code )

    :returns: a :py:class:`tuple` of two elements. The first element is an :py:class:`OAuth2WebServerFlow <oauth2client.client.OAuth2WebServerFlow>` web server flow object. The second element is the redirection URI :py:class:`string <str>` that redirects the user to begin the authorization flow.
    :rtype: tuple
    
    .. seealso::

       * :py:meth:`oauthCheckGoogleCredentials <nprstuff.email.oauthCheckGoogleCredentials>`.
       * :py:meth:`oauthGetOauth2ClientGoogleCredentials <nprstuff.email.oauthGetOauth2ClientGoogleCredentials>`.
       * :py:meth:`oauth_store_google_credentials <nprstuff.email.oauth_store_google_credentials>`.

    .. _Oauth2: https://oauth.net/2
    .. _`Google OAuth2`: https://developers.google.com/identity/protocols/oauth2
    """
    
    #flow = Flow.from_client_secrets_file(
    #    os.path.join( mainDir, 'resources', 'client_secrets.json' ),
    #    scopes = [ 'https://www.googleapis.com/auth/gmail.send',
    #               'https://www.googleapis.com/auth/contacts.readonly',
    #               'https://www.googleapis.com/auth/youtube.readonly',
    #               'https://www.googleapis.com/auth/spreadsheets.readonly', # google spreadsheet scope
    #               'https://www.googleapis.com/auth/musicmanager' ], # this is the gmusicapi one
    #    redirect_uri = "urn:ietf:wg:oauth:2.0:oob" )
    #auth_uri = flow.authorization_url( )
    flow = oauth2client.client.flow_from_clientsecrets(
        os.path.join( resourceDir, 'client_secrets.json' ),
        scope = [ 'https://www.googleapis.com/auth/gmail.send',
                  'https://www.googleapis.com/auth/contacts.readonly' ],
        # 'https://www.googleapis.com/auth/spreadsheets.readonly' ], # google spreadsheet scope readonly
        redirect_uri = "urn:ietf:wg:oauth:2.0:oob" )
    auth_uri = flow.step1_get_authorize_url( )
    return flow, auth_uri

def oauth_store_google_credentials( credentials ):
    """
    Store the `Google OAuth2`_ credentials, in the form of a :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` object, into the SQLite3_ configuration database.
    
    :param credentials: the :py:class:`AccessTokenCredentials <oauth2client.client.AccessTokenCredentials>` object to store into the database.

    .. seealso::

       * :py:meth:`oauthCheckGoogleCredentials <nprstuff.email.oauthCheckGoogleCredentials>`.
       * :py:meth:`oauthGetOauth2ClientGoogleCredentials <nprstuff.email.oauthGetOauth2ClientGoogleCredentials>`.
       * :py:meth:`oauth_generate_google_permission_url <nprstuff.email.oauth_generate_google_permission_url>`.
    """
    val = session.query( NPRStuffConfig ).filter( NPRStuffConfig.service == 'google' ).first( )
    if val is not None:
        session.delete( val )
        session.commit( )
    newval = NPRStuffConfig(
        service = 'google',
        data = json.loads( credentials.to_json( ) ) )
    session.add( newval )
    session.commit( )

class HtmlView( QWebEngineView ):
    """
    A convenient PyQt5_ widget that displays rich and interactive HTML (HTML with CSS and Javascript). This extends :py:class:`QWebEngineView <PyQt5.QtWebEngineWidgets.QWebEngineView>`. This defines new actions, with shortcuts, to move *forward* one page, *backward* one page, or *reset*.

    :param parent: the controlling :py:class:`QWidgert <PyQt5.QtWidgets.QWidget>`, if any.
    :param str htmlString: the input initial rich HTML.

    :var str initHTMLString: this widget has the ability to *reset* to the initial HTML web page used to construct it. This attribute stores that rich HTML as a :py:class:`string <str>`.
    """
    def __init__( self, parent, htmlString = '' ):
        super( HtmlView, self ).__init__( parent )
        self.initHtmlString = htmlString
        self.setHtml( self.initHtmlString )
        #channel = QWebChannel( self )
        #self.page( ).setWebChannel( channel )
        #channel.registerObject( 'thisFormula', self )
        #
        # self.setHtml( myhtml )
        #self.loadFinished.connect( self.on_loadFinished )
        #self.initialized = False
        #
        self._setupActions( )
        self._manager = QNetworkAccessManager( self )

    def _setupActions( self ):
        backAction = QAction( self )
        backAction.setShortcut( 'Shift+Ctrl+1' )
        backAction.triggered.connect( self.back )
        self.addAction( backAction )
        forwardAction = QAction( self )
        forwardAction.setShortcut( 'Shift+Ctrl+2' )
        forwardAction.triggered.connect( self.forward )
        self.addAction( forwardAction )

    def reset( self ):
        """
        Reverts to the initial website.
        """
        self.setHtml( self.initHtmlString )
        
    def on_loadFinished( self ):
        self.initialized = True

    def waitUntilReady( self ):
        """
        A subordinate process that loads all website elements (CSS and Javascript) until done.
        """
        if not self.initialized:
            loop = QEventLoop( )
            self.loadFinished.connect( loop.quit )
            loop.exec_( )
