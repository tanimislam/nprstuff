import calendar, numpy, time, datetime, os
import multiprocessing, multiprocessing.pool
from itertools import chain
from distutils.spawn import find_executable
import urllib.parse as urlparse
from urllib.parse import urlencode
from configparser import ConfigParser, RawConfigParser

def get_firefox_driver( ):
    from selenium import webdriver
    from selenium.webdriver.firefox.options import Options
    geckodriver = find_executable( 'geckodriver' )
    if geckodriver is None:
        raise ValueError("Error, could not find geckodriver to launch Selenium Firefox headless browser." )
    options = Options( )
    options.headless = True
    driver = webdriver.Firefox( options = options )
    return driver

def find_necessary_executables( ):
    """
    :returns: this method searches first for the avconv_, then the FFmpeg_, executable for audiovisual conversion. If it finds either executable, returns a :py:class:`dict` that looks like ``{ 'avconv' : <EXEC_PATH> }``, where ``<EXEC_PATH>`` is the executable's path. If it does NOT find it, returns ``None``.

    .. _avconv: https://en.wikipedia.org/wiki/Libav
    .. _FFmpeg: https://en.wikipedia.org/wiki/FFmpeg
    """
    ffmpeg_exec = None
    for ffmpeg_exc in ('avconv', 'ffmpeg'):
        ffmpeg_exec = find_executable(ffmpeg_exc)
        if ffmpeg_exec is not None: break
    if ffmpeg_exec is None: return None
    #
    return { 'avconv' : ffmpeg_exec }

def store_api_key( npr_API_key ):
    """
    Stores a candidate NPR API key into the configuration file, ``~/.config/nprstuff/nprstuff.conf``, into the ``NPR_DATA`` section and ``apikey`` key.

    :param str npr_API_key: candidate NPR API key.

    .. seealso:: :py:meth:`get_api_key <nprstuff.core.npr_utils.get_api_key>`.
    """
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = os.path.abspath(
        os.path.expanduser( '~/.config/%s' % resource ) )
    absPath = os.path.join( baseConfDir, filename )
    if os.path.isdir( absPath ):
        shutil.rmtree( absPath )
    if not os.path.isfile( absPath ):
        cparser = RawConfigParser( )
    else:
        cparser = ConfigParser( )
        cparser.read( absPath )
    #
    cparser.remove_section( 'NPR_DATA' )
    cparser.add_section('NPR_DATA')
    cparser.set('NPR_DATA', 'apikey', npr_API_key)
    with open( absPath, 'wb') as openfile:
        cparser.write( openfile )
        os.chmod( absPath, 0o600 )
  
def get_api_key( ):
    """
    :returns: the NPR API key, stored in ``~/.config/nprstuff/nprstuff.conf``, under the ``NPR_DATA`` section and ``apikey`` key.

    .. seealso:: :py:meth:`store_api_key <nprstuff.core.npr_utils.store_api_key>`.
    """
    resource = 'nprstuff'
    filename = '%s.conf' % resource
    baseConfDir = os.path.abspath(
        os.path.expanduser( '~/.config/%s' % resource ) )
    absPath = os.path.join( baseConfDir, filename )
    if not os.path.isfile( absPath ):
        raise ValueError("Error, default configuration file = %s does not exist." % absPath )
    cparser = ConfigParser()
    cparser.read( absPath )
    if not cparser.has_section('NPR_DATA'):
        raise ValueError("Error, configuration file has not defined NPR_DATA section.")
    if not cparser.has_option('NPR_DATA', 'apikey'):
        raise ValueError("Error, configuration files has not defined an apikey.")
    npr_api_key = cparser.get('NPR_DATA', 'apikey')
    return npr_api_key
  
def get_decdate(date_s):
    """
    :param str date_s: a *decoded* date string, of the format "DD.MM.YYYY". This is a suffix attached to intermediate files that are created when downloading NPR shows.
    :returns: a :py:class:`datetime <datetime.datetime>` object associated with this date string.
    :rtype: :py:class:`datetime <datetime.datetime>`
    """
    return date_s.strftime('%d.%m.%Y')

def get_NPR_URL(date_s, program_id, NPR_API_key):
    """
    get the NPR API tag for a specific NPR program.
    
    :param str date_s: a date string formatted as "YYYY-MM-DD".
    :param int program_id: the NPR program's integer ID.
    :param str NPR_API_key: the NPR API key.
    :returns: a :py:class:`str` of the exploded URL for REST API calls to the NPR API server.
    :rtype: str
    
    .. deprecated:: no methods call this function any more, instead using the :py:module:`requests` module's cleaner, higher-level functionality of REST API commands.
    """
    nprApiDate = date_s.strftime('%Y-%m-%d')
    result = urlparse.ParseResult(scheme = 'https', netloc = 'api.npr.org', path='/query', params='',
                                  query = urlencode({ 'id' : program_id,
                                                     'date' : nprApiDate,
                                                     'dateType' : 'story',
                                                     'output' : 'NPRML',
                                                     'apiKey' : NPR_API_key }), fragment = '')
    return result.geturl( )

def weekdays_of_month_of_year( year, month ):
    """
    :param int year: input year.
    :param int month: input month as an integer from 1 (January) through 12 (December).
    :returns: a sorted :py:class:`list` of days in a calendar month that are weekdays, each of which ranges from first (1) to last day of month. Each day is an integer :math:`\ge 1`.
    :rtype: list

    .. seealso:: :py:meth:`saturdays_of_month_of_year <nprstuff.core.npr_utils.saturdays_of_month_of_year>`.
    """
    days = sorted(
        filter(lambda day: day != 0,
            numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,0:5].flatten() ) )
    return days

def saturdays_of_month_of_year( year, month ):
    """
    :param int year: input year.
    :param int month: input month as an integer from 1 (January) through 12 (December).
    :returns: a sorted :py:class:`list` of days in a calendar month that are Saturdays, each of which ranges from first (1) to last day of month. Each day is an integer :math:`\ge 1`.
    :rtype: list

    .. seealso:: :py:meth:`weekdays_of_month_of_year <nprstuff.core.npr_utils.weekdays_of_month_of_year>`.
    """
    days = sorted(
        filter(lambda day: day != 0,
            numpy.array( calendar.monthcalendar(year, month), dtype=int)[:,5].flatten() ) )
    return days

def get_time_from_datestring(datestring):
    """
    :param str datestring: a formatted date string, which must be of the form "January 1, 2014".
    :returns: a :py:class:`date <datetime.date>` object represented by that formatted date string.
    :rtype: :py:class:`date <datetime.date>`
    """
    return datetime.datetime.strptime(datestring, '%B %d, %Y').date( )

def get_datestring( date_act ):
    """
    :param datetime date_act: the candidate :py:class:`datetime <datetime.datetime>` to format.
    :returns: a :py:class:`str`, with the format like "January 1, 2014", of this :py:class:`datetime <datetime.datetime>`.
    :rtype: str

    .. seealso:: :py:meth:`get_time_froom_datestring <nprstuff.core.npr_utils.get_time_from_datestring>`.
    """
    return date_act.strftime('%B %d, %Y')

def is_weekday(date_act):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a weekday.
    :rtype: bool
    """
    return date_act.weekday() in list(range(5))
                                    
def is_saturday(date_act):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a Saturday.
    :rtype: bool
    """
    return date_act.weekday() == 5

def is_sunday(dtime):
    """
    :param date date_act: candidate date.
    :returns: whether the :py:class:`date <datetime.date>` is a Sunday.
    :rtype: bool
    """
    return date_act.weekday() == 6

def get_order_number_weekday_in_year(date_act):
    """
    Returns the *1-indexed* order of the weekday associated with a given :py:class:`date <datetime.date>`. NOTE: this object MUST be a weekday.

    :param date date_act: the candidate weekday.

    :returns: a :py:class:`tuple` of *1-indexed* order of the weekday, and total number of weekdays, in the year in which this date exists.
    
    :rtype: tuple

    .. seealso:: 

         * :py:meth:`get_order_number_saturday_in_year <nprstuff.core.npr_utils.get_order_number_saturday_in_year>`.
         * :py:meth:`get_weekday_times_in_year <nprstuff.core.npr_utils.get_weekday_times_in_year>`.
         * :py:meth:`is_weekday <nprstuff.core.npr_utils.is_weekday>`.
    """
    assert( is_weekday(date_act ) )
    year_of_dtime = date_act.year
    all_wkdays_sorted = get_weekday_times_in_year( year_of_dtime )
    num = all_wkdays_sorted.index( date_act )
    return (num+1), len( all_wkdays_sorted )

def get_order_number_saturday_in_year( date_act ):
    """
    Returns the *1-indexed* order of the Saturday associated with a given :py:class:`date <datetime.date>`. NOTE: this object MUST be a Saturday.

    :param date date_act: the candidate Saturday.

    :returns: a :py:class:`tuple` of *1-indexed* order, and total number of Saturdays, in the year in which this Saturday exists.
    
    :rtype: tuple

    .. seealso:: 

         * :py:meth:`get_order_number_weekday_in_year <nprstuff.core.npr_utils.get_order_number_weekday_in_year>`.
         * :py:meth:`get_saturday_times_in_year <nprstuff.core.npr_utils.get_saturday_times_in_year>`.
         * :py:meth:`is_saturday <nprstuff.core.npr_utils.is_saturday>`.
    """
    assert( is_saturday(date_act ) )
    year_of_dtime = date_act.year
    all_saturdays_sorted = get_saturday_times_in_year( year_of_dtime )
    num = all_saturdays_sorted.index( date_act )
    return (num+1), len( all_saturdays_sorted )

def get_saturday_times_in_year(year, getAll = True):
    """
    Returns a sorted :py:class:`list` of Saturdays, as :py:class:`date <datetime.date>` objects for a given year, either *all* the Saturdays or all the Saturdays before now.

    :param int year: the year over which to find the weekdays.
    :param bool getAll: if ``True``, then return *all* the Saturdays. If ``False``, return those Saturdays before today.

    :returns: a sorted :py:class:`list` of Saturdays as a :py:class:`date <datetime.date>` objects.
    
    :rtype: list

    .. seealso:: :py:meth:`get_weekday_times_in_year <nprstuff.core.npr_utils.get_weekday_times_in_year>`.
    """
    nowd = datetime.datetime.now( ).date( )
    initsats = sorted(chain.from_iterable(
        map(lambda year: map(lambda day: datetime.date( year, month, day ), saturdays_of_month_of_year(year, month) ),
            range(1, 13 ) ) ) )
    if getAll: return initsats
    return list(filter(lambda day: dat < nowd, initsats ) )
    
def get_weekday_times_in_year(year, getAll = True):
    """
    Returns a sorted :py:class:`list` of weekdays, as :py:class:`date <datetime.date>` objects for a given year, either *all* the weekdays or all the weekdays before now.

    :param int year: the year over which to find the weekdays.
    :param bool getAll: if ``True``, then return *all* the weekdays. If ``False``, return those weekdays before today.

    :returns: a sorted :py:class:`list` of weekdays as a :py:class:`date <datetime.date>` objects.
    
    :rtype: list

    .. seealso:: :py:meth:`get_saturday_times_in_year <nprstuff.core.npr_utils.get_saturday_times_in_year>`.
    """
    inittimes = sorted(chain.from_iterable(
        map(lambda month: map(lambda day: datetime.date( year, month, day ),
                              weekdays_of_month_of_year( year, month ) ),
            range(1, 13 ) ) ) )
    if getAll: return inittimes
    #
    nowd = datetime.datetime.now( ).date( )
    return list( filter(lambda actd: actd < nowd, inittimes ) )

class NoDaemonProcess(multiprocessing.Process):
  """
  Magic to get multiprocessing to get processes to be able to start daemons.
  
  I copied the code from http://stackoverflow.com/a/8963618/3362358, without
  any real understanding EXCEPT that I am extending a :py:class:`Pool <multiprocessing.Pool>` using an object that always returns ``False``.
  
  This allows one to create a pool of workers that can spawn other processes (by default, :py:module:`multiprocessing` does not
  allow this)
  
  .. seealso:: :py:class:`MyPool <nprstuff.core.npr_utils.MyPool>`.
  """
  # make 'daemon' attribute always return False
  def _get_daemon(self):
    return False
  def _set_daemon(self, value):
    pass
  daemon = property(_get_daemon, _set_daemon)

class MyPool(multiprocessing.pool.Pool):
    """
    A type of :py:class:`Pool <multiprocessing.pool.Pool>` whose processes can spawn other processes, since they use :py:class:`NoDaemonProcess <nprstuff.core.npr_utils.NoDaemonProcess>` inside them.

    .. seealso:: :py:class:`NoDaemonProcess <nprstuff.core.npr_utils.NoDaemonProcess>`.
    """
    Process = NoDaemonProcess
