import os, sys, base64, httplib2, numpy, glob, traceback
import hashlib, requests, io, datetime, logging
import pathos.multiprocessing as multiprocessing
from googleapiclient.discovery import build
#
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.audio import MIMEAudio
from email.mime.image import MIMEImage
#
from nprstuff.email import oauthGetOauth2ClientGoogleCredentials

def get_email_service( verify = True, credentials = None ):
    """
    This returns a working :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails.
    
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails.
    :rtype: :py:class:`Resource <googleapiclient.discovery.Resource>`
    """
    if credentials is None: credentials = oauthGetOauth2ClientGoogleCredentials( )
    assert( credentials is not None )
    http_auth = credentials.authorize( httplib2.Http(
        disable_ssl_certificate_validation = not verify ) )
    email_service = build('gmail', 'v1', http = http_auth,
                          cache_discovery = False )
    return email_service

def get_people_service( verify = True, credentials = None ):
    """
    This returns a working :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google people service used to get a list of one's Google contacts.
    
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    
    :returns: the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google people service.
    :rtype: :py:class:`Resource <googleapiclient.discovery.Resource>`
    """
    if credentials is None: credentials = oauthGetOauth2ClientGoogleCredentials( )
    assert( credentials is not None )
    http_auth = credentials.authorize( httplib2.Http(
        disable_ssl_certificate_validation = not verify ) )
    people_service = build( 'people', 'v1', http = http_auth,
                            cache_discovery = False )
    return people_service
    
def send_email_lowlevel( msg, email_service = None, verify = True ):
    """
    Sends out an email using the `Google Contacts API`_. If process is unsuccessfull, prints out an error message, ``"problem with <TO-EMAIL>"``, where ``<TO-EMAIL>`` is the recipient's email address.

    :param MIMEMultiPart msg: the :py:class:`MIMEMultiPart <email.mime.multipart.MIMEMultiPart>` email message to send. At a high level, this is an email with body, sender, recipients, and optional attachments.
    :param email_service: optional argument, the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails. If ``None``, then generated here.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.

    .. seealso:: :py:meth:`get_email_service <howdy.email.get_email_service>`.

    .. _`Google Contacts API`: https://developers.google.com/contacts/v3
    .. _Ubuntu: https://www.ubuntu.com
    """
    
    data = { 'raw' : base64.urlsafe_b64encode(
        msg.as_bytes( ) ).decode('utf-8') }
    #
    if email_service is None: email_service = get_email_service( verify = verify )
    try: message = email_service.users( ).messages( ).send( userId='me', body = data ).execute( )
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        logging.error('here is exception: %s' % str( e ) )
        logging.error('problem with %s' % msg['To'] )

def get_all_email_contacts_dict( verify = True, people_service = None, pagesize = 4000 ):
    """
    Returns *all* the Google contacts using the `Google Contacts API`_.
    
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param people_service: optional argument, the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google people service used to retrieve one's Google contacts. If ``None``, then generated here.
    :param int pagesize: optional argument, the *maximum* number of candidate contacts to search through. Must be :math:`\ge 1`.
    :returns: a :py:class:`dict` of contacts. The key is the contact name, and the value is the :py:class:`set` of email addresses for that contact.
    :rtype: dict
    """
    if people_service is None: people_service = get_people_service( verify = verify )
    connections = people_service.people( ).connections( ).list(
        resourceName='people/me', personFields='names,emailAddresses',
        pageSize = pagesize ).execute( )
    emails_dict = { }
    for conn in filter(lambda conn: 'names' in conn and 'emailAddresses' in conn,
                       connections['connections']):
        name = conn['names'][0]['displayName']
        emails = set(map(lambda eml: eml['value'], conn['emailAddresses'] ) )
        if name not in emails_dict:
            emails_dict[ name ] = emails
        else:
            new_emails = emails | emails_dict[ name ]
            emails_dict[ name ] = new_emails
    while 'nextPageToken' in connections: 
        connections = people_service.people( ).connections( ).list(
            resourceName='people/me', personFields='names,emailAddresses',
            pageToken = connections['nextPageToken'], pageSize = pagesize ).execute( )
        for conn in filter(lambda conn: 'names' in conn and 'emailAddresses' in conn,
                           connections['connections']):
            name = conn['names'][0]['displayName']
            emails = set(map(lambda eml: eml['value'], conn['emailAddresses'] ) )
            if name not in emails_dict:
                emails_dict[ name ] = emails
            else:
                new_emails = emails | emails_dict[ name ]
                emails_dict[ name ] = new_emails
    return emails_dict


def test_email( subject = None, htmlstring = None, verify = True ):
    """
    Sends a test email to the Plex_ user's email address.
    
    :param str subject: optional argument. The email subject. If not defined, the subject is ``"Plex Email Newsletter for <MONTH> <YEAR>"``.
    :param str htmlstring: optional argument. The email body as an HTML :py:class:`str` document. If not defined, the body is ``"This is a test."``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    """
    assert( emailAddress is not None ), "Error, email address must not be None"
    if emailName is None: emailString = emailAddress
    else: emailString = '%s <%s>' % ( emailName, emailAddress )
    fromEmail = emailString
    if subject is None:
        subject = titlecase.titlecase( 'Plex Email Newsletter For %s' % mydate.strftime( '%B %Y' ) )
    msg = MIMEMultipart( )
    msg['From'] = fromEmail
    msg['Subject'] = subject
    msg['To'] = emailAddress
    if htmlstring is None: body = MIMEText( 'This is a test.' )
    else: body = MIMEText( htmlstring, 'html', 'utf-8' )
    msg.attach( body )
    send_email_lowlevel( msg, verify = verify )

def send_collective_email_full(
    mainHTML, subject, fromEmail, to_emails, cc_emails, bcc_emails, verify = True,
    email_service = None ):
    """
    Sends the HTML email to the following ``TO`` recipients, ``CC`` recipients, and ``BCC`` recipients altogether. It uses the `GMail API`_.

    :param str mainHTML: the email body as an HTML :py:class:`string <str>` document.
    :param str subject: the email subject.
    :param str fromEmail: the `RFC 2047`_ sender's email with name.
    :param set to_emails: the `RFC 2047`_ :py:class:`set` of ``TO`` recipients.
    :param set cc_emails: the `RFC 2047`_ :py:class:`set` of ``CC`` recipients.
    :param set bcc_emails: the `RFC 2047`_ :py:class:`set` of ``BCC`` recipients.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param email_service: optional argument, the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails. If ``None``, then generated here.

    .. _`RFC 2047`: https://tools.ietf.org/html/rfc2047.html
    """
    #
    ## get the RFC 2047 sender stuff
    msg = MIMEMultipart( )
    msg[ 'From' ] = fromEmail
    msg[ 'Subject' ] = subject
    msg[ 'To' ] = ', '.join( sorted(to_emails ) )
    msg[ 'Cc' ] = ', '.join( sorted(cc_emails ) )
    msg[ 'Bcc'] = ', '.join( sorted(bcc_emails ) )
    logging.info( 'to_emails: %s.' % msg['To'] )
    logging.info( 'cc_emails: %s.' % msg['Cc'] )
    logging.info('bcc_emails: %s.' % msg['Bcc'])
    msg.attach( MIMEText( mainHTML, 'html', 'utf-8' ) )
    send_email_lowlevel( msg, email_service = email_service, verify = verify )

def send_individual_email_full(
    mainHTML, subject, emailAddress, name = None, attach = None,
    attachName = None, attachType = 'txt', verify = True, email_service = None ):
    """
    Sends the HTML email, with optional *single* attachment, to a single recipient email address, using the `GMail API`_. Unlike :py:meth:`send_individual_email_full_withsingleattach <howdy.email.email.send_individual_email_full_withsingleattach>`, the attachment type is *also* set.

    :param str mainHTML: the email body as an HTML :py:class:`str` document.
    :param str subject: the email subject.
    :param str emailAddress: the recipient email address.
    :param str name: optional argument. If given, the recipient's name.
    :param date mydate: optional argument. The :py:class:`date <datetime.date>` at which the email is sent. Default is :py:meth:`now( ) <datetime.datetime.now>`.
    :param str attach: optional argument. If defined, the Base64_ encoded attachment.
    :param str attachName: optional argument. The :py:class:`list` of attachment names, if there is an attachment. If defined, then ``attachData`` must also be defined.
    :param str attachType: the attachment type. Default is ``txt``.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param email_service: optional argument, the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails. If ``None``, then generated here.

    :raise AssertionError: if the current Plex_ account user's email address does not exist.
    """
    assert( emailAddress is not None ), "Error, email address must not be None"
    emailName = ''
    if name is not None: emailName = name
    fromEmail = formataddr( ( emailName, emailAddress ) )
    msg = MIMEMultipart( )
    msg['From'] = fromEmail
    msg['Subject'] = subject
    if name is None:
        msg['To'] = emailAddress
        htmlstring = mainHTML
    else:
        msg['To'] = formataddr( ( name, emailAddress ) )
        firstname = name.split()[0].strip()
        htmlstring = re.sub( 'Hello Friend,', 'Hello %s,' % firstname, mainHTML )
    body = MIMEText( htmlstring, 'html', 'utf-8' )
    msg.attach( body )
    if attach is not None and attachName is not None:
        att = MIMEApplication( attach, _subtype = 'text' )
        att.add_header( 'content-disposition', 'attachment', filename = attachName )
        msg.attach( att )
    send_email_lowlevel( msg, email_service = email_service, verify = verify )


def send_individual_email(
        mainHTML, email, name = None,
        mydate = datetime.datetime.now().date( ),
        verify = True, email_service = None ):
    """
    sends the HTML email to a single recipient email address using the `GMail API`_. The subject is ``"Plex Email Newsletter for <MONTH> <YEAR>"``.

    :param str mainHTML: the email body as an HTML :py:class:`str` document.
    :param str email: the recipient email address.
    :param str name: optional argument. If given, the recipient's name.
    :param date mydate: optional argument. The :py:class:`date <datetime.date>` at which the email is sent. Default is :py:meth:`now( ) <datetime.datetime.now>`.
    :param bool verify: optional argument, whether to verify SSL connections. Default is ``True``.
    :param email_service: optional argument, the :py:class:`Resource <googleapiclient.discovery.Resource>` representing the Google email service used to send and receive emails. If ``None``, then generated here.

    :raise AssertionError: if the current Plex_ account user's email address does not exist.
    """
    assert( emailAddress is not None ), "Error, email address must not be None"
    if emailName is None: fromEmail = emailAddress
    else: fromEmail = '%s <%s>' % ( emailName, emailAddress )
    subject = titlecase.titlecase( 'Plex Email Newsletter For %s' % mydate.strftime( '%B %Y' ) )
    msg = MIMEMultipart( )
    msg['From'] = fromEmail
    msg['Subject'] = subject
    if name is None:
        msg['To'] = email
        htmlstring = mainHTML
    else:
        msg['To'] = '%s <%s>' % ( name, email )
        firstname = name.split()[0].strip()
        htmlstring = re.sub( 'Hello Friend,', 'Hello %s,' % firstname, mainHTML )
    #
    body = MIMEText( htmlstring, 'html', 'utf-8' )
    msg.attach( body )
    send_email_lowlevel( msg, email_service = email_service, verify = verify )
