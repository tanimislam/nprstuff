import os, sys, base64, httplib2, numpy, glob, traceback
import hashlib, requests, io, datetime, logging
import pathos.multiprocessing as multiprocessing
from googleapiclient.discovery import build
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
